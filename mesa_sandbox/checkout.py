"""Funções puras de exemplo para um teste de CI sem dependências."""


def subtotal_cents(unit_price_cents: int, quantity: int) -> int:
    """Calcula um subtotal inteiro em centavos, sem arredondamento monetário."""
    if type(unit_price_cents) is not int or type(quantity) is not int:
        raise TypeError("preço e quantidade precisam ser inteiros")
    if unit_price_cents < 0 or quantity < 0:
        raise ValueError("preço e quantidade não podem ser negativos")
    return unit_price_cents * quantity
