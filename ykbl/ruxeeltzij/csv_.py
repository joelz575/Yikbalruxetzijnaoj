import os

import numpy as np
import pandas as pd

from ykbl.samajibäl import _, rubanom_ramaj
from ykbl.setul import Setul
from .ruxeeltzij import RuxeelTzij, TununemRetalJaloj


class RucheelRamaj(object):
    def __init__(ri, rucheel, rubeyal=None):
        ri.rucheel = rucheel
        ri.rubeyal = rubeyal


class RucheelKolibäl(object):
    def __init__(ri, rucheel, setul, jalonïk=None):
        ri.rucheel = rucheel
        ri.setul = setul
        ri.jalonïk = jalonïk or {}


class RuxeelTzijCSV(RuxeelTzij):
    def __init__(ri, rubi, rochochibäl, tununem, retamabäl, kolibäl, ramaj):
        ri.rochochibäl = rochochibäl
        ri.cache = f'{ri.rochochibäl}.parquet'

        ri.kolibäl = kolibäl
        ri.ramaj = ramaj

        super().__init__(rubi, tununem=tununem, retamabäl=retamabäl)

    def jalixïk_cache(ri):
        return os.path.isfile(ri.cache) and os.path.getmtime(ri.rochochibäl) < os.path.getmtime(ri.cache)

    def rejqalem(ri, retal_jaloj, kolibäl, ramaj, chabäl):

        retal_jaloj = ri._rusikxïk_retal_jaloj(retal_jaloj)
        if not retal_jaloj:
            return

        rucheel = ri._rucheel_csv(retal_jaloj)
        rucheel_kolibäl, rucheel_ramaj = _("K'olib'äl", chabäl), _("Ramaj", chabäl)

        if ri.jalixïk_cache():
            tzj = pd.read_parquet(ri.cache, columns=rucheel)
        else:
            tzj = pd.read_csv(ri.rochochibäl, usecols=rucheel)
            tzj.to_parquet(ri.cache)

        if isinstance(ri.kolibäl, RucheelKolibäl):
            tzj[rucheel_kolibäl] = tzj[ri.kolibäl.rucheel].map(ri.kolibäl.jalonïk).fillna(tzj[ri.kolibäl.rucheel])
        elif ri.kolibäl:
            tzj[rucheel_kolibäl] = str(ri.kolibäl)
        else:
            tzj[rucheel_kolibäl] = np.nan

        if isinstance(ri.ramaj, RucheelRamaj):
            tzj[ri.ramaj.rucheel] = pd.to_datetime(tzj[ri.ramaj.rucheel], format=ri.ramaj.rubeyal)
        elif ri.ramaj:
            tzj[rucheel_ramaj] = rubanom_ramaj(ri.ramaj)
        else:
            tzj[rucheel_ramaj] = np.nan

        tzj = tzj.rename(columns=ri._kibi_retaljaloj_rucheel(chabäl))

        if kolibäl is not None:  # Chi ninb'an: tiqatz'u chi setul kolibäl == ri.setul
            if isinstance(kolibäl, Setul):
                taq_kolibäl = kolibäl.taq_etal
            else:
                taq_kolibäl = kolibäl.retal

            tzj = tzj[tzj[rucheel_kolibäl].isin(taq_kolibäl)]

        for rtl in retal_jaloj:
            tnm = next(tnm for tnm in ri.tununem if tnm.retal_jaloj == rtl)
            tzj[rtl.rubi_pa(chabäl)] *= tnm
        return tzj

    def _rucheel_csv(ri, retal_jaloj):
        rucheel = [tnm.rucheel for tnm in ri.tununem if tnm.retal_jaloj in retal_jaloj]
        if isinstance(ri.ramaj, RucheelRamaj):
            rucheel.append(ri.ramaj.rucheel)
        if isinstance(ri.kolibäl, RucheelKolibäl):
            rucheel.append(ri.kolibäl.rucheel)

        return rucheel

    def _kibi_retaljaloj_rucheel(ri, chabäl):
        kibi = {tnm.rucheel: tnm.retal_jaloj.rubi_pa(chabäl) for tnm in ri.tununem}

        if isinstance(ri.ramaj, RucheelRamaj):
            kibi.update({ri.ramaj.rucheel: _("Ramaj", chabäl)})
        if isinstance(ri.kolibäl, RucheelKolibäl):
            kibi.update({ri.kolibäl.rucheel: _("K'olib'äl", chabäl)})

        return kibi
