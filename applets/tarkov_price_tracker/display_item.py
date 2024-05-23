from typing import Optional, Dict


class DisplayItem:
    """Represent a 64x16 row on the matrix"""

    def __init__(
        self, name: str, price: int, icon_link: str, change_last_48h_percent: float
    ) -> None:
        """Initialise a DisplayItem"""
        self.name = name
        self.price = price
        self.icon_link = icon_link
        self.change_last_48h_percent = change_last_48h_percent

    @staticmethod
    def get_highest_trader_price(data: Dict) -> int:
        """Get the highest price offered by a trader for a given item"""
        items = data.get("data", {}).get("items", [])
        max_price = max(
            (
                offer.get("price", 0)
                for item in items
                for offer in item.get("sellFor", [])
            ),
            default=-1,
        )
        return max_price

    @classmethod
    def from_graphql(cls, data: Dict) -> Optional["DisplayItem"]:
        """Create a DisplayItem from a GraphQL query response"""
        items = data.get("data", {}).get("items", [])
        if items:
            item = items[0]
            short_name = item.get("shortName")
            price = item.get("avg24hPrice")
            if not price:
                price = cls.get_highest_trader_price(data)
            icon_link = item.get("iconLink", "")
            change_last_48h_percent = item.get("changeLast48hPercent", 0)
            return cls(
                name=short_name,
                price=price,
                icon_link=icon_link,
                change_last_48h_percent=change_last_48h_percent,
            )
        return None
