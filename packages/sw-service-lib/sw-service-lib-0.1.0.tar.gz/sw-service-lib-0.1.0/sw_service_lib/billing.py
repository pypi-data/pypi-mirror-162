from __future__ import annotations


class BillingTransaction:
    def __init__(
        self,
        id: str = None,
        status: str = None,
        description: str = None,
        memo: str = None,
        amount: float = None,
        unit: str = None,
    ):
        self.id = id
        self.status = status
        self.description = description
        self.memo = memo
        self.amount = amount
        self.unit = unit
        return

    @classmethod
    def from_dict(cls, res: dict) -> BillingTransaction:
        b = BillingTransaction()
        b.id = res["id"]
        b.status = res["status"]
        b.description = res["description"]
        b.memo = res["memo"]
        b.amount = res["amount"]
        b.unit = res["unit"]
        return b
