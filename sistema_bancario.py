import time
import datetime
import json 

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

    def validar_monto(self, monto):
        if not isinstance(monto, (int, float)):
            raise MontoInvalidoError("El monto debe ser un número")
        if monto > 0:
            return True
        else:
            raise MontoInvalidoError("El monto debe ser mayor a cero")

    def depositar(self, monto):
        self.validar_monto(monto)
        self.saldo += monto
        self.historial_transacciones.append({
                "tipo": "depósito",
                "monto": monto,
                "fecha": datetime.datetime.now()
        })

    def retirar(self, monto):
        self.validar_monto(monto)
        self.validar_saldo(monto)
        self.saldo -= monto
        self.historial_transacciones.append({
            "tipo": "retiro",
            "monto": monto,
            "fecha": datetime.datetime.now()
            })

    def transferir(self, monto, cuenta_destino):
        if not isinstance(cuenta_destino, Cuenta):
            raise CuentaNoEncontradaError("La cuenta destino no es válida")
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
        historial_convertido = []
        for transaccion in self.historial_transacciones:
            nueva_transaccion = {
                "tipo": transaccion["tipo"],
                "monto": transaccion["monto"],
                "fecha": transaccion["fecha"].isoformat()
            }
            historial_convertido.append(nueva_transaccion)

        return {
            "numero_cuenta": self.numero_cuenta,
            "saldo": self.saldo,
            "contrasena": self.contrasena,
            "historial_transacciones": historial_convertido,
            "intentos_fallidos": self.intentos_fallidos
        }

    @classmethod
    def desde_diccionario(cls, datos):
        cuenta_nueva = cls(datos["numero_cuenta"], datos["contrasena"])
        cuenta_nueva.saldo = datos["saldo"]
        historial_restaurado = []
        for transaccion in datos["historial_transacciones"]:
            nueva_transaccion = {
            "tipo": transaccion["tipo"],
            "monto": transaccion["monto"],
            "fecha": datetime.datetime.fromisoformat(transaccion["fecha"])
            }
            historial_restaurado.append(nueva_transaccion)
        cuenta_nueva.historial_transacciones = historial_restaurado
        cuenta_nueva.intentos_fallidos = datos["intentos_fallidos"]
        return cuenta_nueva

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

    @classmethod
    def desde_diccionario(cls, datos):
        cliente_nuevo = cls(datos["nombre"])
        for numero, datos_cuenta in datos["cuentas"].items():
            cuenta_nueva = Cuenta.desde_diccionario(datos_cuenta)
            cliente_nuevo.agregar_cuenta(cuenta_nueva)
        return cliente_nuevo

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

    def realizar_transferencia(self, numero_origen, numero_destino, monto):
        cuenta_origen = self.buscar_cuenta(numero_origen)
        cuenta_destino = self.buscar_cuenta(numero_destino)
        cuenta_origen.transferir(monto, cuenta_destino)

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

    def guardar_json(self, nombre_archivo="datos_banco.json"):
        datos = self.a_diccionario()
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    @classmethod
    def cargar_json(cls, nombre_archivo="datos_banco.json"):
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        sistema_nuevo = cls()
        for nombre, datos_cliente in datos["clientes"].items():
            cliente = Cliente.desde_diccionario(datos_cliente)
            sistema_nuevo.agregar_cliente(cliente)
        for numero, datos_cuenta in datos["cuentas"].items():
            cuenta = Cuenta.desde_diccionario(datos_cuenta)
            sistema_nuevo.base_sistema[numero] = cuenta
        return sistema_nuevo

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


banco = SistemaBancario()
mi_cliente = Cliente("Yamil")
banco.agregar_cliente(mi_cliente)
banco.agregar_cuenta(mi_cliente, Cuenta("1234567890", "1234"))
registrar_cuenta = banco.agregar_cuenta(mi_cliente, Cuenta("0987654321", "5678"))
depositar = banco.buscar_cuenta("1234567890").depositar(1000)
guardar = banco.guardar_json()
banco_cargado = SistemaBancario.cargar_json()
print(banco_cargado.buscar_cuenta("1234567890").saldo)