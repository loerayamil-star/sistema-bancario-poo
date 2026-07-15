import time
import datetime

# =====

class Cuenta:
    def __init__(self, numero_cuenta, contrasena):
        self.numero_cuenta = numero_cuenta
        self.saldo = 0
        self.contrasena = contrasena
        self.historial_transacciones = []
        self.intentos_fallidos = 0

    def validar_saldo(self, monto):
        if self.intentos_fallidos >= 5:
            raise IntentosExcedidosError("Se han excedido los intentos de transacción")
        
        if self.saldo >= monto:
            return True
        else:
            self.intentos_fallidos += 1
            raise SaldoInsuficienteError("Saldo insuficiente, intente con una menor cantidad o recargue su cuenta")

    

class SaldoInsuficienteError(Exception):
    pass

class IntentosExcedidosError(Exception):
    pass