function formToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function submitJsonForm(form) {
  const message = form.querySelector("[data-form-message]");
  message.textContent = "Saving...";

  const response = await fetch(form.dataset.action, {
    method: form.dataset.method || "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formToObject(form)),
  });

  const payload = await response.json();

  if (!response.ok) {
    message.textContent = payload.error || "Save failed.";
    return;
  }

  if (payload.location) {
    window.location.href = payload.location;
    return;
  }

  message.textContent = "Saved.";
}

async function submitIngredientForm(form) {
  const message = form.querySelector("[data-form-message]");
  const ingredients = [...form.querySelectorAll("[data-ingredient-id]")].map((row) => {
    return {
      id: row.dataset.ingredientId,
      supplier: row.querySelector('[name="supplier"]').value,
      supplier_lot: row.querySelector('[name="supplier_lot"]').value,
      internal_lot: row.querySelector('[name="internal_lot"]').value,
      actual_quantity: row.querySelector('[name="actual_quantity"]').value,
      unit: row.querySelector('[name="unit"]').value,
      expiration_date: row.querySelector('[name="expiration_date"]').value,
      notes: row.querySelector('[name="notes"]').value,
    };
  });

  message.textContent = "Saving...";

  const response = await fetch(form.dataset.action, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ingredients }),
  });

  const payload = await response.json();

  if (!response.ok) {
    message.textContent = payload.error || "Save failed.";
    return;
  }

  message.textContent = "Saved.";
}

document.addEventListener("submit", (event) => {
  const jsonForm = event.target.closest("[data-json-form]");
  if (jsonForm) {
    event.preventDefault();
    submitJsonForm(jsonForm);
    return;
  }

  const ingredientForm = event.target.closest("[data-ingredient-form]");
  if (ingredientForm) {
    event.preventDefault();
    submitIngredientForm(ingredientForm);
  }
});
