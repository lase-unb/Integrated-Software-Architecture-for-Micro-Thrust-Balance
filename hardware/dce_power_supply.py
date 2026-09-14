# -*- coding: utf-8 -*-
"""
Driver da fonte programável do DCE (Dispositivo de Calibração Eletrostática).
Objetivo: comandar voltagem via SCPI e ler de volta o valor medido na saída.
"""

import numpy as np

VOLT_MAX = 1000.0  # limite de segurança do DCE (RF14), mesmo valor de interface/main.py


class RigolDP932U:
    """
    Driver real da fonte RIGOL DP932U via SCPI/USB (PyVISA).
    Comandos conforme o Programming Guide oficial (DP900 series):
    :APPL, :OUTP[:STATe], :MEAS[:SCALar]:ALL[:DC]?, *IDN?
    """

    def __init__(self, resource=None):
        import pyvisa
        rm = pyvisa.ResourceManager("@py")
        if resource is None:
            candidatos = [r for r in rm.list_resources() if "USB" in r]
            if not candidatos:
                raise RuntimeError("Nenhuma fonte RIGOL encontrada via USB.")
            resource = candidatos[0]
        self.inst = rm.open_resource(resource)

    def identificar(self):
        return self.inst.query("*IDN?").strip()

    def set_voltage(self, canal, volts, corrente=None):
        if corrente is None:
            self.inst.write(f":APPL {canal},{volts}")
        else:
            self.inst.write(f":APPL {canal},{volts},{corrente}")

    def output(self, canal, ligado):
        estado = "ON" if ligado else "OFF"
        self.inst.write(f":OUTP {canal},{estado}")

    def medir(self, canal):
        """Retorna (V, I, P) medidos de fato na saída do canal."""
        resp = self.inst.query(f":MEAS:ALL? {canal}")
        v, i, p = (float(x) for x in resp.strip().split(","))
        return v, i, p

    def fechar(self):
        self.inst.close()


class FontePowerSupplySimulada:
    """
    Substituto sem hardware para RigolDP932U — mesma interface, usado para
    testar a rotina de calibração via DCE (calibration/dce_calibration.py)
    sem a fonte física conectada.
    """

    def __init__(self, ruido_v=0.01):
        self.ruido_v = ruido_v
        self._estado = {}

    def identificar(self):
        return "SIMULADOR,FontePowerSupplySimulada,0,1.0"

    def set_voltage(self, canal, volts, corrente=None):
        self._estado[canal] = {"v": volts, "on": self._estado.get(canal, {}).get("on", False)}

    def output(self, canal, ligado):
        self._estado.setdefault(canal, {"v": 0.0})["on"] = ligado

    def medir(self, canal):
        v_nominal = self._estado.get(canal, {}).get("v", 0.0)
        v_medido = v_nominal + np.random.normal(0, self.ruido_v)
        return v_medido, 0.0, 0.0

    def ultimo_valor(self, canal):
        return self._estado.get(canal, {}).get("v", 0.0)

    def fechar(self):
        pass
