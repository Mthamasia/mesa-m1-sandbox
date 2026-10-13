"""Funções puras de exemplo para um teste de CI sem dependências."""


def subtotal_cents(unit_price_cents: int, quantity: int) -> int:
    """Calcula um subtotal inteiro em centavos, sem arredondamento monetário."""
    if type(unit_price_cents) is not int or type(quantity) is not int:
        raise TypeError("preço e quantidade precisam ser inteiros")
    if unit_price_cents < 0 or quantity < 0:
        raise ValueError("preço e quantidade não podem ser negativos")
    return unit_price_cents * quantity


def apply_discount_cents(subtotal: int, discount_basis_points: int) -> int:
    """Aplica desconto em pontos-base (0 a 10_000), arredondando para baixo."""
    if type(subtotal) is not int or type(discount_basis_points) is not int:
        raise TypeError("subtotal e desconto precisam ser inteiros")
    if subtotal < 0:
        raise ValueError("subtotal não pode ser negativo")
    if not 0 <= discount_basis_points <= 10_000:
        raise ValueError("desconto deve estar entre 0 e 10_000 pontos-base")
    return subtotal * (10_000 - discount_basis_points) // 10_000
