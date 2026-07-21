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

    def a_diccionario(self):
        return {
            "numero_cuenta": self.numero_cuenta,
            "saldo": self.saldo,
            "contrasena": self.contrasena,
            "historial_transacciones": self.historial_transacciones,
            "intentos_fallidos": self.intentos_fallidos
        }

class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre
        self.cuentas = {}

    def agregar_cuenta(self, cuenta):
        self.cuentas[cuenta.numero_cuenta] = cuenta

    def consultar_cuentas(self):
        return self.cuentas
    
    def a_diccionario(self):
        cuentas_convertidas ={}
        for numero, cuenta in self.cuentas.items():
            cuentas_convertidas[numero] = cuenta.a_diccionario()
        return {
            "nombre": self.nombre,
            "cuentas": cuentas_convertidas
        }

class SistemaBancario:
    def __init__(self):
        self.base_sistema = {}
        self.base_clientes = {}

    def agregar_cliente(self, cliente):
        self.base_clientes[cliente.nombre] = cliente

    def agregar_cuenta(self, cliente, cuenta):
        self.base_sistema[cuenta.numero_cuenta] = cuenta
        cliente.agregar_cuenta(cuenta)

    def buscar_cliente(self, nombre):
        cliente = self.base_clientes.get(nombre)
        if cliente:
            return cliente
        else:
            raise ClienteNoEncontradoError("Cliente no encontrado")

    def buscar_cuenta(self, numero_cuenta):
        cuenta = self.base_sistema.get(numero_cuenta)
        if cuenta:
            return cuenta
        else:
            raise CuentaNoEncontradaError("Cuenta no encontrada")
        
    def a_diccionario(self):
        clientes_convertidos = {}
        for nombre, cliente in self.base_clientes.items():
            clientes_convertidos[nombre] = cliente.a_diccionario()

        cuentas_convertidas = {}
        for numero, cuenta in self.base_sistema.items():
            cuentas_convertidas[numero] = cuenta.a_diccionario()
            
        return {
            "clientes": clientes_convertidos,
            "cuentas": cuentas_convertidas
        }

class ClienteNoEncontradoError(Exception):
    pass

class CuentaNoEncontradaError(Exception):
    pass

class SaldoInsuficienteError(Exception):
    pass

class IntentosExcedidosError(Exception):
    pass
class MontoInvalidoError(Exception):
    pass