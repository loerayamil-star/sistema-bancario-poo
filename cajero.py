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

    def depositar(self, monto):
        if monto > 0:
            self.saldo += monto
            self.historial_transacciones.append({
                "tipo": "depósito",
                "monto": monto,
                "fecha": datetime.datetime.now()
            })
        else:
            raise MontoInvalidoError("El monto a depositar es invalido")

    def retirar(self, monto):
        self.validar_saldo(monto)
        self.saldo -= monto
        self.historial_transacciones.append({
            "tipo": "retiro",
            "monto": monto,
            "fecha": datetime.datetime.now()
            })

    def transferir(self, monto, cuenta_destino):
        self.retirar(monto)
        cuenta_destino.depositar(monto)
        self.historial_transacciones.append({
            "tipo": "transferencia",
            "monto": monto,
            "fecha": datetime.datetime.now(),
            "cuenta_destino": cuenta_destino.numero_cuenta[-4:]
        })

    def consultar_historial(self):
        return self.historial_transacciones

class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre
        self.cuentas = {}

    def agregar_cuenta(self, cuenta):
        self.cuentas[cuenta.numero_cuenta] = cuenta


class SaldoInsuficienteError(Exception):
    pass

class IntentosExcedidosError(Exception):
    pass
class MontoInvalidoError(Exception):
    pass