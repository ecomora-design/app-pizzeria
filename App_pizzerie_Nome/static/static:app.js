let selectedItems = [];

async function loadMenu() {
  const response = await fetch("/menu");
  const menu = await response.json();

  const menuList = document.getElementById("menu-list");
  menuList.innerHTML = "";

  menu.forEach(item => {
    const div = document.createElement("div");
    div.className = "menu-item";
    div.innerHTML = `
      <strong>${item.name}</strong> - €${item.price.toFixed(2)}<br>
      <small>${item.category}</small><br><br>
      <input type="number" min="1" value="1" id="qty-${item.id}">
      <button type="button" onclick="addToOrder(${item.id})">Aggiungi</button>
    `;
    menuList.appendChild(div);
  });
}

function addToOrder(menuItemId) {
  const qtyInput = document.getElementById(`qty-${menuItemId}`);
  const quantity = parseInt(qtyInput.value);

  const existing = selectedItems.find(i => i.menu_item_id === menuItemId);
  if (existing) {
    existing.quantity += quantity;
  } else {
    selectedItems.push({
      menu_item_id: menuItemId,
      quantity: quantity
    });
  }

  alert("Prodotto aggiunto all'ordine");
}

document.getElementById("order-form").addEventListener("submit", async function(e) {
  e.preventDefault();

  const payload = {
    customer_name: document.getElementById("customer_name").value,
    phone: document.getElementById("phone").value,
    order_type: document.getElementById("order_type").value,
    address: document.getElementById("address").value || null,
    requested_time: document.getElementById("requested_time").value || null,
    notes: document.getElementById("notes").value || null,
    items: selectedItems
  };

  const response = await fetch("/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  const resultBox = document.getElementById("result");

  if (response.ok) {
    resultBox.innerText = `Ordine confermato! ID: ${result.order_id} - Totale: €${result.total}`;
    selectedItems = [];
    document.getElementById("order-form").reset();
  } else {
    resultBox.innerText = `Errore: ${result.detail || "qualcosa è andato storto"}`;
  }
});

loadMenu();