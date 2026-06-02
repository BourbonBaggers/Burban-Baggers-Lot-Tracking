function formToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function submitJsonForm(form) {
  const message = form.querySelector("[data-form-message]");
  const releasedCount = form.querySelector("[data-released-count]");
  const submitButton = form.querySelector('button[type="submit"]');

  if (submitButton) {
    submitButton.disabled = true;
  }

  message.textContent = "Saving...";

  try {
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

    if (releasedCount && payload.released_count !== undefined) {
      releasedCount.textContent = payload.released_count;
    }

    message.textContent = "Saved.";
  } catch {
    message.textContent = "Save failed.";
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
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
    return;
  }

  const checkpointForm = event.target.closest("[data-checkpoint-form]");
  if (checkpointForm) {
    event.preventDefault();
    submitCheckpointForm(checkpointForm);
    return;
  }

  const uploadForm = event.target.closest("[data-upload-form]");
  if (uploadForm) {
    event.preventDefault();
    submitUploadForm(uploadForm);
  }
});

document.addEventListener("click", (event) => {
  const row = event.target.closest("[data-checkpoint-id]");
  if (!row) {
    return;
  }

  document.querySelectorAll("[data-checkpoint-id]").forEach((item) => {
    item.classList.remove("selected-row");
  });
  row.classList.add("selected-row");

  const form = document.querySelector("[data-checkpoint-form]");
  if (form) {
    form.querySelector('[name="checkpoint_id"]').value = row.dataset.checkpointId;
  }
});

async function submitCheckpointForm(form) {
  const message = form.querySelector("[data-form-message]");
  const checkpointId = form.querySelector('[name="checkpoint_id"]').value;
  const row = document.querySelector(`[data-checkpoint-id="${checkpointId}"]`);

  if (!row) {
    message.textContent = "Select a checkpoint row first.";
    return;
  }

  const payload = {
    inspection_date: row.querySelector('[name="inspection_date"]').value,
    ph: row.querySelector('[name="ph"]').value,
    brix: row.querySelector('[name="brix"]').value,
    passed: row.querySelector('[name="passed"]').value,
    notes: row.querySelector('[name="notes"]').value,
    appearance: form.querySelector('[name="appearance"]').value,
    aroma: form.querySelector('[name="aroma"]').value,
    taste_notes: form.querySelector('[name="taste_notes"]').value,
    seal_condition: form.querySelector('[name="seal_condition"]').value,
    spoilage_observations: form.querySelector('[name="spoilage_observations"]').value,
  };

  message.textContent = "Saving...";

  const response = await fetch(`/api/checkpoints/${checkpointId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();

  if (!response.ok) {
    message.textContent = result.error || "Save failed.";
    return;
  }

  row.querySelector(".status-pill").textContent = result.status;
  message.textContent = "Saved.";
}

async function submitUploadForm(form) {
  const message = form.querySelector("[data-form-message]");
  const submitButton = form.querySelector('button[type="submit"]');
  const data = new FormData(form);

  if (submitButton) {
    submitButton.disabled = true;
  }
  message.textContent = "Uploading...";

  try {
    const response = await fetch(form.dataset.action, {
      method: "POST",
      body: data,
    });
    const payload = await response.json();

    if (!response.ok) {
      message.textContent = payload.error || "Upload failed.";
      return;
    }

    window.location.href = payload.location;
  } catch {
    message.textContent = "Upload failed.";
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
}
