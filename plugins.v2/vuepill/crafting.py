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
_MAX_EXCHANGE_BATCH = 100
_MAX_GIFT_QUANTITY = 500
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


def _validate_recipe(output_item, rows_by_output, used_ids):
    matching_rows = rows_by_output.get(output_item, ())
    if not matching_rows:
        return None, "缺少%s配方" % output_item
    if len(matching_rows) != 1:
        return None, "检测到重复产物"

    raw_recipe = matching_rows[0]
    if "supported" in raw_recipe and raw_recipe["supported"] is not True:
        return None, "存在不受支持的配方"

    craft_id = raw_recipe.get("craft_id")
    if isinstance(craft_id, bool) or not isinstance(craft_id, int) or craft_id <= 0:
        return None, "配方编号无效"
    if craft_id in used_ids and used_ids[craft_id] != output_item:
        return None, "检测到重复配方编号"

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

    used_ids[craft_id] = output_item
    return {
        "craft_id": craft_id,
        "output_item": output_item,
        "ingredients": ingredients,
    }, ""


def _prepare_recipes(recipes):
    if recipes is None or isinstance(recipes, (dict, str, bytes)):
        return None, None, "配方数据无效"
    try:
        recipe_rows = iter(recipes)
    except TypeError:
        return None, None, "配方数据无效"

    rows_by_output = {}
    try:
        for raw_recipe in recipe_rows:
            if not isinstance(raw_recipe, dict):
                continue
            output_item = _clean_name(raw_recipe.get("output_item"))
            if not output_item:
                continue
            rows_by_output.setdefault(output_item, []).append(raw_recipe)
    except Exception:
        return None, None, "配方数据读取失败"

    root_recipe, error = _validate_recipe(_MAGIC_PILL, rows_by_output, {})
    if root_recipe is None:
        return None, None, error
    return rows_by_output, root_recipe, ""


def _topological_plan_order(plan, preferred_order, by_output):
    planned_ids = set(plan)
    recipes_by_id = {
        recipe["craft_id"]: recipe for recipe in by_output.values()
    }
    candidates = [craft_id for craft_id in preferred_order if craft_id in planned_ids]
    candidates.extend(craft_id for craft_id in plan if craft_id not in candidates)
    ranks = {craft_id: index for index, craft_id in enumerate(candidates)}
    indegrees = {craft_id: 0 for craft_id in candidates}
    dependents = {craft_id: [] for craft_id in candidates}

    for craft_id in candidates:
        seen_dependencies = set()
        for ingredient_name in recipes_by_id[craft_id]["ingredients"]:
            dependency = by_output.get(ingredient_name)
            dependency_id = dependency["craft_id"] if dependency else None
            if dependency_id not in planned_ids or dependency_id in seen_dependencies:
                continue
            seen_dependencies.add(dependency_id)
            indegrees[craft_id] += 1
            dependents[dependency_id].append(craft_id)

    ready = [craft_id for craft_id in candidates if indegrees[craft_id] == 0]
    ordered = []
    while ready:
        ready.sort(key=ranks.__getitem__)
        craft_id = ready.pop(0)
        ordered.append(craft_id)
        for dependent_id in dependents[craft_id]:
            indegrees[dependent_id] -= 1
            if indegrees[dependent_id] == 0:
                ready.append(dependent_id)

    return ordered if len(ordered) == len(candidates) else None


def _related_inventory_items(rows_by_output, root_recipe):
    related_items = set()
    visited_outputs = {_MAGIC_PILL}
    pending_items = list(root_recipe["ingredients"])
    while pending_items:
        item_name = pending_items.pop()
        related_items.add(item_name)
        if item_name in visited_outputs:
            continue
        visited_outputs.add(item_name)

        for raw_recipe in rows_by_output.get(item_name, ()):
            raw_ingredients = raw_recipe.get("ingredients")
            if not isinstance(raw_ingredients, dict):
                continue
            pending_items.extend(
                ingredient_name
                for ingredient_name in (
                    _clean_name(raw_name) for raw_name in raw_ingredients
                )
                if ingredient_name
            )
    related_items.discard(_MAGIC_PILL)
    return related_items


def _attempt_plan(inventory, rows_by_output, root_recipe, target):
    stock = dict(inventory)
    plan = {}
    order = []
    missing = {}
    validated_by_output = {_MAGIC_PILL: root_recipe}
    used_ids = {root_recipe["craft_id"]: _MAGIC_PILL}
    active_outputs = set()
    failure_reason = ""

    def fail(reason):
        nonlocal failure_reason
        if not failure_reason:
            failure_reason = reason
        return False

    def provide(item_name, quantity):
        available = stock.get(item_name, 0)
        used = min(available, quantity)
        if used:
            stock[item_name] = available - used
        remaining = quantity - used
        if remaining <= 0:
            return True

        if item_name in active_outputs:
            return fail("检测到循环依赖")

        if item_name not in rows_by_output:
            missing[item_name] = missing.get(item_name, 0) + remaining
            return False
        recipe = validated_by_output.get(item_name)
        if recipe is None:
            recipe, error = _validate_recipe(item_name, rows_by_output, used_ids)
            if recipe is None:
                return fail(error)
            validated_by_output[item_name] = recipe
        return craft(recipe, remaining)

    def craft(recipe, quantity):
        output_item = recipe["output_item"]
        if output_item in active_outputs:
            return fail("检测到循环依赖")

        active_outputs.add(output_item)
        ingredients_ready = True
        try:
            for ingredient_name, required in recipe["ingredients"].items():
                if not provide(ingredient_name, required * quantity):
                    ingredients_ready = False
        finally:
            active_outputs.remove(output_item)
        if not ingredients_ready:
            return False

        craft_id = recipe["craft_id"]
        if craft_id not in plan:
            plan[craft_id] = 0
            order.append(craft_id)
        plan[craft_id] += quantity
        return True

    if not craft(root_recipe, target):
        return _empty_result(
            reason=failure_reason or "库存不足或缺少前置配方",
            missing=missing,
        )

    order = _topological_plan_order(plan, order, validated_by_output)
    if order is None:
        return _empty_result(reason="炼造步骤依赖排序失败")

    plan = {craft_id: plan[craft_id] for craft_id in order}
    recipes_by_id = {
        recipe["craft_id"]: recipe for recipe in validated_by_output.values()
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
        rows_by_output, root_recipe, error = _prepare_recipes(recipes)
        if rows_by_output is None:
            return _empty_result(reason=error)
        stock = _inventory_map(inventory)

        if parsed_target is not None:
            return _attempt_plan(
                stock,
                rows_by_output,
                root_recipe,
                parsed_target,
            )

        related_items = _related_inventory_items(rows_by_output, root_recipe)
        upper_bound = sum(stock.get(item_name, 0) for item_name in related_items)
        low = 0
        high = upper_bound
        while low < high:
            middle = (low + high + 1) // 2
            attempt = _attempt_plan(stock, rows_by_output, root_recipe, middle)
            if attempt["max_count"] == middle:
                low = middle
            else:
                high = middle - 1

        if low <= 0:
            return _attempt_plan(stock, rows_by_output, root_recipe, 1)
        return _attempt_plan(stock, rows_by_output, root_recipe, low)
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

    maximum = min(maximum, _MAX_EXCHANGE_BATCH)
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
    cap_value = min(cap_value, _MAX_GIFT_QUANTITY)
    stock = _inventory_map(inventory).get(name, 0)
    return min(stock, cap_value)
