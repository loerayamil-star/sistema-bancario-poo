import pytest

from sistema_bancario import (
    Cuenta,
    CuentaNoEncontradaError,
    MontoInvalidoError,
    SaldoInsuficienteError,
)


def test_depositar_aumenta_saldo():
    cuenta = Cuenta("123456", "1234")
    cuenta.depositar(100)
    assert cuenta.saldo == 100


def test_depositar_monto_negativo():
    cuenta = Cuenta("123456", "1234")
    with pytest.raises(MontoInvalidoError):
        cuenta.depositar(-50)


def test_retirar_mas_de_lo_disponible():
    cuenta = Cuenta("123456", "1234")
    cuenta.depositar(100)
    with pytest.raises(SaldoInsuficienteError):
        cuenta.retirar(150)


def test_retirar_monto_negativo():
    cuenta = Cuenta("123456", "1234")
    with pytest.raises(MontoInvalidoError):
        cuenta.retirar(-30)


def test_transferir_cuenta_destino_invalida():
    cuenta_origen = Cuenta("123456", "1234")
    cuenta_origen.depositar(100)
    cuenta_destino = "cuenta_invalida"
    with pytest.raises(CuentaNoEncontradaError):
        cuenta_origen.transferir(50, cuenta_destino)
