"""sms_module_hilink.py — v4

• Convertit automatiquement les numéros « 06… » → « +33… » pour éviter
  l’erreur Hi‑Link 113004.
• Limite les envois : **un SMS maxi toutes les 5 min pendant qu’une même
  alarme reste active** ; dès que le flag repasse à 0, la fenêtre est remise à
  zéro et un nouveau SMS partira immédiatement si l’alarme se relance.
"""

from __future__ import annotations

import html
import threading
import time
import xml.etree.ElementTree as ET
from typing import Iterable, List

import requests

import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12

import unicodedata
import re

_GSM7 = (
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1BÆæßÉ "
    " !\"#¤%&'()*+,-./0123456789:;<=>?¡"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿"
    "abcdefghijklmnopqrstuvwxyzäöñüà"
)

def to_gsm7(text: str) -> str:
    """Enlève accents et caractères non GSM-7."""
    txt = unicodedata.normalize("NFD", text)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return re.sub(fr"[^{re.escape(_GSM7)}]", " ", txt)
# ---------------------------------------------------------------------------
# Hi‑Link modem wrapper
# ---------------------------------------------------------------------------

class HiLinkError(RuntimeError):
    """Raised when the modem returns an <error> code."""

class HiLinkModem:
    """Minimal helper to send SMS via /api/sms/send-sms."""

    def __init__(self, base_url: str = "http://192.168.8.1") -> None:
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def _cookie_token(self) -> tuple[str, str]:
        xml = self._session.get(f"{self.base_url}/api/webserver/SesTokInfo", timeout=3).text
        root = ET.fromstring(xml)
        return root.findtext("SesInfo", ""), root.findtext("TokInfo", "")

    def send_sms(self, phone: str, message: str) -> None:
        if phone.startswith("0") and len(phone) == 10:
            phone = "+33" + phone[1:]
        cookie, token = self._cookie_token()
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<request><Index>-1</Index>'
            f'<Phones><Phone>{phone}</Phone></Phones>'
            '<Sca></Sca>'
            f'<Content>{html.escape(message)}</Content>'
            '<Length>-1</Length><Reserved>1</Reserved><Date>-1</Date></request>'
        )
        r = self._session.post(
            f"{self.base_url}/api/sms/send-sms",
            headers={"Cookie": cookie, "__RequestVerificationToken": token},
            data=body,
            timeout=5,
        )
        if r.status_code != 200 or "<response>OK</response>" not in r.text:
            raise HiLinkError(r.text.strip())

# ---------------------------------------------------------------------------
# SMSModule thread
# ---------------------------------------------------------------------------
def clean_phone(num):
        num = num.strip().replace(" ", "")
        if num.startswith("00"):
            num = "+" + num[2:]
        if num.startswith("0") and len(num) == 10:
            num = "+33" + num[1:]
        return num
        
class SMSModule(threading.Thread):
    """Polls flags in *alarme_* / *defaut_* and sends throttled SMS."""

    # --- class‑level mappings (must stay **inside** the class) ----------------
    _ALARMS = [
        (alarme_1.Alarme1, 1, "Alarme radiologique sur détecteur 1"),
        (alarme_2.Alarme2, 2, "Alarme radiologique sur détecteur 2"),
        (alarme_3.Alarme3, 3, "Alarme radiologique sur détecteur 3"),
        (alarme_4.Alarme4, 4, "Alarme radiologique sur détecteur 4"),
        (alarme_5.Alarme5, 5, "Alarme radiologique sur détecteur 5"),
        (alarme_6.Alarme6, 6, "Alarme radiologique sur détecteur 6"),
        (alarme_7.Alarme7, 7, "Alarme radiologique sur détecteur 7"),
        (alarme_8.Alarme8, 8, "Alarme radiologique sur détecteur 8"),
        (alarme_9.Alarme9, 9, "Alarme radiologique sur détecteur 9"),
        (alarme_10.Alarme10, 10, "Alarme radiologique sur détecteur 10"),
        (alarme_11.Alarme11, 11, "Alarme radiologique sur détecteur 11"),
        (alarme_12.Alarme12, 12, "Alarme radiologique sur détecteur 12"),
    ]

    _DEFAUTS = [
        (defaut_1.Defaut_1, 1, "Alarme technique sur détecteur 1"),
        (defaut_2.Defaut_2, 2, "Alarme technique sur détecteur 2"),
        (defaut_3.Defaut_3, 3, "Alarme technique sur détecteur 3"),
        (defaut_4.Defaut_4, 4, "Alarme technique sur détecteur 4"),
        (defaut_5.Defaut_5, 5, "Alarme technique sur détecteur 5"),
        (defaut_6.Defaut_6, 6, "Alarme technique sur détecteur 6"),
        (defaut_7.Defaut_7, 7, "Alarme technique sur détecteur 7"),
        (defaut_8.Defaut_8, 8, "Alarme technique sur détecteur 8"),
        (defaut_9.Defaut_9, 9, "Alarme technique sur détecteur 9"),
        (defaut_10.Defaut_10, 10, "Alarme technique sur détecteur 10"),
        (defaut_11.Defaut_11, 11, "Alarme technique sur détecteur 11"),
        (defaut_12.Defaut_12, 12, "Alarme technique sur détecteur 12"),
    ]

    _THROTTLE = 300  # seconds = 300  # secondes

    def __init__(
        self,
        Nom_portique: str,
        phone_numbers: Iterable[str],
        modem_url: str = "http://192.168.8.1",
        poll_period: float = 1.0,
    ) -> None:
        super().__init__(daemon=True)
        self.nom_portique = Nom_portique
        self.phone_numbers = [clean_phone(n) for n in phone_numbers if n]
        self.poll_period = poll_period
        self.modem = HiLinkModem(modem_url)
        self._stop = threading.Event()
        self._last_sent: dict[str, float] = {}
        self._flag_active: dict[str, bool] = {}

    # ------------------------------------------------------------------
    
    def _send(self, key: str, msg: str) -> None:
        now = time.time()
        if now - self._last_sent.get(key, 0) < self._THROTTLE:
            return
        self._last_sent[key] = now
        for num in self.phone_numbers:
            try:
                self.modem.send_sms(num, msg)
                print(f"SMS envoyé à {num} ({key})")
                time.sleep(10)
            except Exception as exc:
                print(f"Échec d'envoi SMS à {num}: {exc}")

    # ------------------------------------------------------------------
    def run(self):
        tpl = f"Message portique Berthold GeV5 – {self.nom_portique} – {{msg}}"
        while not self._stop.is_set():
            # ---- radiological alarms ---------------------------------
            for module, idx, text in self._ALARMS:
                flag = getattr(module, "alarme_resultat").get(idx, 0)
                key = f"A{idx}"
                if flag in (1, 2):
                    self._flag_active[key] = True
                    self._send(key, tpl.format(msg=text))
                else:  # flag == 0
                    if self._flag_active.pop(key, False):
                        self._last_sent.pop(key, None)  # reset throttle

            # ---- technical alarms ------------------------------------
            for module, idx, text in self._DEFAUTS:
                flag = getattr(module, "eta_defaut").get(idx, 0)
                key = f"T{idx}"
                if flag in (1, 2):
                    self._flag_active[key] = True
                    self._send(key, tpl.format(msg=text))
                else:
                    if self._flag_active.pop(key, False):
                        self._last_sent.pop(key, None)  # reset throttle
                        
            time.sleep(1)
