# `tests/` — Тестирование

## Запуск

```bash
pytest tests/ -v --cov=src
```
## Покрытие требований
- Корректность равного и пропорционального разделения
- Обработка пустых списков (0 участников, 0 товаров)
- Сериализация/десериализация Decimal и datetime
- HTTP-статусы при ошибках (404, 400)

## Пример теста
```python
def test_equal_split():
    bill = Bill()
    bill.add_user("Анна")
    bill.add_user("Борис")
    bill.items.append(Item("Пицца", Decimal("1000"), ["u1", "u2"]))
    bill.payments.append(Payment("u1", Decimal("1000")))
    
    debts = compute_debts(bill, "equal")
    assert debts == [("u2", "u1", Decimal("500"))]
```