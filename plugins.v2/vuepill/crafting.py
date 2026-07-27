"""Dependency-free calculations for Vue-魔丸 crafting and exchanges."""

import math
import re


__all__ = [
    "inventory_to_map",
    "compute_magic_pill_plan",
    "exchange_batches",
    "max_gift_quantity",
]


_MAGIC_PILL = "魔丸"
_INTEGER_WITH_COMMAS = re.compile(r"\d{1,3}(?:,\d{3})+")


def _integer_value(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isfinite(value) and value.is_integer():
            return int(value)
        return None
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    sign = ""
    if text[0] in "+-":
        sign, text = text[0], text[1:]
    if not text:
        return None
    if "," in text:
        if _INTEGER_WITH_COMMAS.fullmatch(text) is None:
            return None
        text = text.replace(",", "")
    elif not text.isdigit():
        return None
    try:
        return int(sign + text)
    except (TypeError, ValueError, OverflowError):
        return None


def _non_negative_value(value):
    parsed = _integer_value(value)
    if parsed is None or parsed < 0:
        return 0
    return parsed


def _clean_name(value):
    if not isinstance(value, str):
        return ""
    return value.strip()


def inventory_to_map(items, reserve_magic_pill_count=0) -> dict:
    """Convert parser inventory rows into a safe, aggregated stock mapping."""

    if isinstance(items, dict):
        rows = (items,) if "name" in items else ()
    elif items is None or isinstance(items, (str, bytes)):
        rows = ()
    else:
        try:
            rows = iter(items)
        except TypeError:
            rows = ()

    inventory = {}
    for item in rows:
        if not isinstance(item, dict):
            continue
        name = _clean_name(item.get("name"))
        if not name:
            continue
        count = _non_negative_value(item.get("count", 0))
        inventory[name] = inventory.get(name, 0) + count

    reserve = _non_negative_value(reserve_magic_pill_count)
    if _MAGIC_PILL in inventory:
        inventory[_MAGIC_PILL] = max(0, inventory[_MAGIC_PILL] - reserve)
    return inventory


def _inventory_map(inventory):
    if not isinstance(inventory, dict):
        return inventory_to_map(inventory)
    if "name" in inventory and "count" in inventory:
        return inventory_to_map((inventory,))

    result = {}
    for raw_name, raw_count in inventory.items():
        name = _clean_name(raw_name)
        if not name:
            continue
        result[name] = result.get(name, 0) + _non_negative_value(raw_count)
    return result


def _empty_result(reason="", missing=None):
    return {
        "max_count": 0,
        "plan": {},
        "steps": [],
        "missing": dict(missing or {}),
        "reason": reason,
    }


def _prepare_recipes(recipes):
    if recipes is None or isinstance(recipes, (dict, str, bytes)):
        return None, "配方数据无效"
    try:
        recipe_rows = iter(recipes)
    except TypeError:
        return None, "配方数据无效"

    by_output = {}
    seen_ids = set()
    for raw_recipe in recipe_rows:
        if not isinstance(raw_recipe, dict):
            return None, "配方数据无效"
        if "supported" in raw_recipe and raw_recipe["supported"] is not True:
            return None, "存在不受支持的配方"

        craft_id = raw_recipe.get("craft_id")
        if isinstance(craft_id, bool) or not isinstance(craft_id, int) or craft_id <= 0:
            return None, "配方编号无效"
        if craft_id in seen_ids:
            return None, "检测到重复配方编号"

        output_item = _clean_name(raw_recipe.get("output_item"))
        if not output_item:
            return None, "配方产物无效"
        if output_item in by_output:
            return None, "检测到重复产物"

        raw_ingredients = raw_recipe.get("ingredients")
        if not isinstance(raw_ingredients, dict) or not raw_ingredients:
            return None, "配方材料无效"
        ingredients = {}
        for raw_name, raw_quantity in raw_ingredients.items():
            ingredient_name = _clean_name(raw_name)
            if not ingredient_name or ingredient_name in ingredients:
                return None, "配方材料无效"
            if (
                isinstance(raw_quantity, bool)
                or not isinstance(raw_quantity, int)
                or raw_quantity <= 0
            ):
                return None, "材料数量必须为正整数"
            ingredients[ingredient_name] = raw_quantity

        seen_ids.add(craft_id)
        by_output[output_item] = {
            "craft_id": craft_id,
            "output_item": output_item,
            "ingredients": ingredients,
        }

    if _MAGIC_PILL not in by_output:
        return None, "缺少魔丸配方"
    if _has_recipe_cycle(by_output):
        return None, "检测到循环依赖"
    return by_output, ""


def _has_recipe_cycle(by_output):
    states = {}

    def visit(output_item):
        state = states.get(output_item, 0)
        if state == 1:
            return True
        if state == 2:
            return False

        states[output_item] = 1
        for ingredient_name in by_output[output_item]["ingredients"]:
            if ingredient_name in by_output and visit(ingredient_name):
                return True
        states[output_item] = 2
        return False

    try:
        return any(visit(output_item) for output_item in by_output)
    except RecursionError:
        return True


def _attempt_plan(inventory, by_output, target):
    stock = dict(inventory)
    plan = {}
    order = []
    missing = {}

    def provide(item_name, quantity):
        available = stock.get(item_name, 0)
        used = min(available, quantity)
        if used:
            stock[item_name] = available - used
        remaining = quantity - used
        if remaining <= 0:
            return True

        recipe = by_output.get(item_name)
        if recipe is None:
            missing[item_name] = missing.get(item_name, 0) + remaining
            return False
        return craft(recipe, remaining)

    def craft(recipe, quantity):
        ingredients_ready = True
        for ingredient_name, required in recipe["ingredients"].items():
            if not provide(ingredient_name, required * quantity):
                ingredients_ready = False
        if not ingredients_ready:
            return False

        craft_id = recipe["craft_id"]
        if craft_id not in plan:
            plan[craft_id] = 0
            order.append(craft_id)
        plan[craft_id] += quantity
        return True

    root_recipe = by_output[_MAGIC_PILL]
    if not craft(root_recipe, target):
        return _empty_result(
            reason="库存不足或缺少前置配方",
            missing=missing,
        )

    recipes_by_id = {
        recipe["craft_id"]: recipe for recipe in by_output.values()
    }
    steps = [
        {
            "craft_id": craft_id,
            "output_item": recipes_by_id[craft_id]["output_item"],
            "count": plan[craft_id],
        }
        for craft_id in order
    ]
    return {
        "max_count": target,
        "plan": plan,
        "steps": steps,
        "missing": {},
        "reason": "",
    }


def compute_magic_pill_plan(inventory, recipes, target=None) -> dict:
    """Build a dependency-ordered plan for newly crafted magic pills."""

    if target is not None:
        parsed_target = _integer_value(target)
        if parsed_target is None:
            return _empty_result(reason="目标数量无效")
        if parsed_target <= 0:
            return _empty_result()
    else:
        parsed_target = None

    try:
        by_output, error = _prepare_recipes(recipes)
        if by_output is None:
            return _empty_result(reason=error)
        stock = _inventory_map(inventory)

        if parsed_target is not None:
            return _attempt_plan(stock, by_output, parsed_target)

        upper_bound = sum(
            count for item_name, count in stock.items() if item_name != _MAGIC_PILL
        )
        low = 0
        high = upper_bound
        while low < high:
            middle = (low + high + 1) // 2
            attempt = _attempt_plan(stock, by_output, middle)
            if attempt["max_count"] == middle:
                low = middle
            else:
                high = middle - 1

        if low <= 0:
            return _attempt_plan(stock, by_output, 1)
        return _attempt_plan(stock, by_output, low)
    except Exception:
        return _empty_result(reason="炼造计划计算失败")


def exchange_batches(current, reserve, max_per_request=100) -> list:
    """Split the safely exchangeable pills into positive request batches."""

    current_value = _integer_value(current)
    reserve_value = _integer_value(reserve)
    maximum = _integer_value(max_per_request)
    if (
        current_value is None
        or reserve_value is None
        or maximum is None
        or current_value < 0
        or reserve_value < 0
        or maximum <= 0
        or current_value <= reserve_value
    ):
        return []

    exchangeable = current_value - reserve_value
    full_batches, remainder = divmod(exchangeable, maximum)
    batches = [maximum] * full_batches
    if remainder:
        batches.append(remainder)
    return batches


def max_gift_quantity(inventory, item_name, cap=500) -> int:
    """Return the giftable stock without exceeding the configured cap."""

    name = _clean_name(item_name)
    cap_value = _integer_value(cap)
    if not name or cap_value is None or cap_value <= 0:
        return 0
    stock = _inventory_map(inventory).get(name, 0)
    return min(stock, cap_value)
