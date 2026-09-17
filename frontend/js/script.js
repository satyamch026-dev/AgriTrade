/* =========================================================
   AGRITRADE - FRONTEND
   Flask + MySQL Backend API
   ========================================================= */

const API_BASE_URL = 'http://127.0.0.1:5000';

const API_ENDPOINTS = {
  dashboard: `${API_BASE_URL}/api/dashboard`,
  products: `${API_BASE_URL}/api/products`
};

let currentProducts = [];
let editingProductId = null;


/* =========================================================
   API SERVICE FUNCTIONS
   ========================================================= */

async function getProducts(search = '') {
  const url = `${API_ENDPOINTS.products}?search=${encodeURIComponent(search)}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Unable to load products');
  }

  return await response.json();
}


async function createProduct(product) {
  const response = await fetch(API_ENDPOINTS.products, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(product)
  });

  if (!response.ok) {
    throw new Error('Unable to create product');
  }

  return await response.json();
}


async function updateProduct(id, product) {
  const response = await fetch(`${API_ENDPOINTS.products}/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(product)
  });

  if (!response.ok) {
    throw new Error('Unable to update product');
  }

  return await response.json();
}


async function deleteProductRequest(id) {
  const response = await fetch(
    `${API_ENDPOINTS.products}/${id}`,
    {
      method: 'DELETE'
    }
  );

  if (!response.ok) {
    throw new Error('Unable to delete product');
  }

  return await response.json();
}


async function getDashboardData() {
  const response = await fetch(API_ENDPOINTS.dashboard);

  if (!response.ok) {
    throw new Error('Unable to load dashboard data');
  }

  return await response.json();
}


/* =========================================================
   DASHBOARD
   ========================================================= */

async function initDashboard() {

  let data;

  try {
    data = await getDashboardData();
  } catch (err) {
    console.error('Dashboard API Error:', err);
    return;
  }

  setText('statTotalProducts', data.totalProducts);
  setText(
    'statTotalCustomers',
    formatNumber(data.totalCustomers)
  );

  setText(
    'statTotalSuppliers',
    formatNumber(data.totalSuppliers)
  );

  setText(
    'statTotalSales',
    formatRupees(data.totalSales)
  );

  setText(
    'statTotalPurchases',
    formatRupees(data.totalPurchases)
  );

  setText(
    'statCurrentStock',
    `${formatNumber(data.currentStock)} kg`
  );

  renderLowStock(data.lowStockProducts || []);
  renderRecentTransactions(data.recentTransactions || []);
  renderSalesChart(data.salesChart);
}


/* =========================================================
   HELPER FUNCTIONS
   ========================================================= */

function setText(id, value) {

  const element = document.getElementById(id);

  if (element) {
    element.textContent = value;
  }
}


function formatNumber(value) {

  const num = Number(value) || 0;

  return num.toLocaleString('en-IN', {
    maximumFractionDigits: 2
  });
}


function formatRupees(value) {

  const num = Number(value) || 0;

  if (num >= 10000000) {
    return `₹${(num / 10000000).toFixed(2)} Cr`;
  }

  if (num >= 100000) {
    return `₹${(num / 100000).toFixed(1)} Lakh`;
  }

  return `₹${formatNumber(num)}`;
}


function escapeHtml(value) {

  return String(value ?? '').replace(
    /[&<>'"]/g,
    char => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[char])
  );
}


/* =========================================================
   LOW STOCK
   ========================================================= */

function renderLowStock(items) {

  const container = document.getElementById('lowStockList');

  if (!container) {
    return;
  }

  if (!items.length) {
    container.innerHTML = `
      <div class="empty-state">
        No low stock products
      </div>
    `;

    return;
  }

  container.innerHTML = items.map(item => `
    <div class="stock-row">

      <div>
        <strong>${escapeHtml(item.name)}</strong>
        <span>${escapeHtml(item.category)}</span>
      </div>

      <b>
        ${formatNumber(item.stock)}
        ${escapeHtml(item.unit)}
      </b>

      <em class="status status-low">
        Low
      </em>

    </div>
  `).join('');
}


/* =========================================================
   RECENT TRANSACTIONS
   ========================================================= */

function renderRecentTransactions(transactions) {

  const tableBody = document.getElementById(
    'recentTransactionsBody'
  );

  if (!tableBody) {
    return;
  }

  if (!transactions.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7">
          No recent transactions
        </td>
      </tr>
    `;

    return;
  }

  tableBody.innerHTML = transactions.map(tx => {

    const statusClass =
      tx.status === 'Completed'
        ? 'status-good'
        : 'status-pending';

    return `
      <tr>

        <td class="strong-cell">
          ${escapeHtml(tx.invoice)}
        </td>

        <td>
          ${escapeHtml(tx.customer)}
        </td>

        <td>
          ${escapeHtml(tx.product)}
        </td>

        <td>
          ${escapeHtml(tx.date)}
        </td>

        <td>
          ${formatNumber(tx.quantity)}
          ${escapeHtml(tx.unit)}
        </td>

        <td class="amount">
          ₹${formatNumber(tx.amount)}
        </td>

        <td>
          <span class="status ${statusClass}">
            ${escapeHtml(tx.status)}
          </span>
        </td>

      </tr>
    `;

  }).join('');
}


/* =========================================================
   SALES CHART
   ========================================================= */

function renderSalesChart(chart) {

  const canvas = document.getElementById('salesChart');

  if (
    !canvas ||
    typeof Chart === 'undefined' ||
    !chart
  ) {
    return;
  }

  new Chart(canvas, {

    type: 'line',

    data: {

      labels: chart.labels,

      datasets: [
        {
          label: 'Sales',

          data: chart.values,

          borderColor: '#2f7d4a',

          backgroundColor:
            'rgba(47, 125, 74, 0.08)',

          borderWidth: 2,

          fill: true,

          tension: 0.35,

          pointRadius: 3,

          pointHoverRadius: 5,

          pointBackgroundColor: '#2f7d4a'
        }
      ]
    },

    options: {

      responsive: true,

      maintainAspectRatio: false,

      plugins: {

        legend: {
          display: false
        },

        tooltip: {

          callbacks: {

            label: context =>
              ` ₹${Number(context.raw)
                .toLocaleString('en-IN')}`
          }
        }
      },

      scales: {

        y: {

          beginAtZero: true,

          ticks: {

            callback: value =>
              `₹${(value / 100000).toFixed(1)}L`,

            color: '#8a948d',

            font: {
              size: 10
            }
          },

          grid: {
            color: '#edf1ed'
          },

          border: {
            display: false
          }
        },

        x: {

          ticks: {

            color: '#8a948d',

            font: {
              size: 10
            }
          },

          grid: {
            display: false
          },

          border: {
            display: false
          }
        }
      }
    }
  });
}


/* =========================================================
   PRODUCTS / INVENTORY
   ========================================================= */

async function initProductsPage() {

  const tableBody =
    document.getElementById('productTableBody');

  const searchInput =
    document.getElementById('productSearch');

  const addButton =
    document.getElementById('addProductBtn');

  const modal =
    document.getElementById('productModal');

  const form =
    document.getElementById('productForm');

  if (
    !tableBody ||
    !searchInput ||
    !addButton ||
    !modal ||
    !form
  ) {
    return;
  }


  async function render() {

    try {

      currentProducts =
        await getProducts(searchInput.value);

      renderProductRows(currentProducts);

    } catch (err) {

      console.error('Products API Error:', err);

      tableBody.innerHTML = `
        <tr>
          <td colspan="11">
            Unable to load products.
          </td>
        </tr>
      `;
    }
  }


  searchInput.addEventListener(
    'input',
    render
  );


  addButton.addEventListener(
    'click',
    () => openModal()
  );


  const closeButton =
    document.getElementById('closeModalBtn');

  const cancelButton =
    document.getElementById('cancelModalBtn');


  if (closeButton) {
    closeButton.addEventListener(
      'click',
      closeModal
    );
  }


  if (cancelButton) {
    cancelButton.addEventListener(
      'click',
      closeModal
    );
  }


  modal.addEventListener(
    'click',
    event => {

      if (event.target === modal) {
        closeModal();
      }

    }
  );


  form.addEventListener(
    'submit',
    async event => {

      event.preventDefault();

      const data = new FormData(form);


      const product = {

        name:
          String(data.get('name') || '').trim(),

        category:
          data.get('category'),

        variety:
          String(data.get('variety') || '').trim(),

        unit:
          data.get('unit'),

        stock:
          Number(data.get('stock')),

        purchasePrice:
          Number(data.get('purchasePrice')),

        sellingPrice:
          Number(data.get('sellingPrice')),

        minimumStock:
          Number(data.get('minimumStock'))
      };


      try {

        if (editingProductId !== null) {

          await updateProduct(
            editingProductId,
            product
          );

        } else {

          await createProduct(product);

        }

      } catch (err) {

        console.error(err);

        alert(
          'Could not save the product. Please try again.'
        );

        return;
      }


      form.reset();

      closeModal();

      await render();

    }
  );


  await render();
}


/* =========================================================
   RENDER PRODUCTS
   ========================================================= */

function renderProductRows(products) {

  const tableBody =
    document.getElementById('productTableBody');

  const emptyState =
    document.getElementById('emptyProducts');

  const count =
    document.getElementById('productCount');


  if (!tableBody) {
    return;
  }


  if (!products.length) {

    tableBody.innerHTML = '';

  } else {

    tableBody.innerHTML =
      products.map(product => {

        const status =
          Number(product.stock) <=
          Number(product.minimumStock)
            ? 'Low'
            : 'Good';

        const statusClass =
          status === 'Low'
            ? 'status-low'
            : 'status-good';


        return `
          <tr>

            <td class="strong-cell">
              ${product.id}
            </td>

            <td class="strong-cell">
              ${escapeHtml(product.name)}
            </td>

            <td>
              ${escapeHtml(product.category)}
            </td>

            <td>
              ${escapeHtml(product.variety)}
            </td>

            <td>
              ${escapeHtml(product.unit)}
            </td>

            <td>
              ${formatNumber(product.stock)}
              ${escapeHtml(product.unit)}
            </td>

            <td>
              ₹${formatNumber(product.purchasePrice)}
            </td>

            <td class="amount">
              ₹${formatNumber(product.sellingPrice)}
            </td>

            <td>
              ${formatNumber(product.minimumStock)}
              ${escapeHtml(product.unit)}
            </td>

            <td>
              <span class="status ${statusClass}">
                ${status}
              </span>
            </td>

            <td>

              <div class="action-buttons">

                <button
                  class="icon-button"
                  type="button"
                  title="Edit"
                  onclick="editProduct(${product.id})"
                >
                  <i class="fa-solid fa-pen"></i>
                </button>

                <button
                  class="icon-button delete"
                  type="button"
                  title="Delete"
                  onclick="deleteProduct(${product.id})"
                >
                  <i class="fa-solid fa-trash"></i>
                </button>

              </div>

            </td>

          </tr>
        `;

      }).join('');
  }


  if (count) {

    count.textContent =
      `${products.length} product${
        products.length === 1 ? '' : 's'
      }`;
  }


  if (emptyState) {

    emptyState.hidden =
      products.length !== 0;
  }
}


/* =========================================================
   PRODUCT MODAL
   ========================================================= */

function openModal(product = null) {

  const modal =
    document.getElementById('productModal');

  const form =
    document.getElementById('productForm');

  const title =
    document.getElementById('modalTitle');


  if (!modal || !form) {
    return;
  }


  const submitBtn =
    form.querySelector(
      'button[type="submit"]'
    );


  editingProductId =
    product ? product.id : null;


  if (product) {

    if (title) {
      title.textContent = 'Edit Product';
    }


    if (submitBtn) {

      submitBtn.innerHTML =
        '<i class="fa-solid fa-floppy-disk"></i> Save Changes';
    }


    form.elements['name'].value =
      product.name;

    form.elements['category'].value =
      product.category;

    form.elements['variety'].value =
      product.variety;

    form.elements['unit'].value =
      product.unit;

    form.elements['stock'].value =
      product.stock;

    form.elements['purchasePrice'].value =
      product.purchasePrice;

    form.elements['sellingPrice'].value =
      product.sellingPrice;

    form.elements['minimumStock'].value =
      product.minimumStock;

  } else {

    if (title) {
      title.textContent = 'Add Product';
    }


    if (submitBtn) {

      submitBtn.innerHTML =
        '<i class="fa-solid fa-plus"></i> Add Product';
    }


    form.reset();
  }


  modal.hidden = false;

  document.body.style.overflow = 'hidden';


  const nameInput =
    document.querySelector(
      '#productForm input[name="name"]'
    );


  if (nameInput) {
    nameInput.focus();
  }
}


/* =========================================================
   CLOSE MODAL
   ========================================================= */

function closeModal() {

  const modal =
    document.getElementById('productModal');

  if (!modal) {
    return;
  }


  modal.hidden = true;

  document.body.style.overflow = '';

  editingProductId = null;
}


/* =========================================================
   EDIT PRODUCT
   ========================================================= */

function editProduct(id) {

  const product =
    currentProducts.find(
      p => Number(p.id) === Number(id)
    );


  if (product) {
    openModal(product);
  }
}


/* =========================================================
   DELETE PRODUCT
   ========================================================= */

async function deleteProduct(id) {

  const product =
    currentProducts.find(
      p => Number(p.id) === Number(id)
    );


  const name =
    product
      ? product.name
      : `#${id}`;


  if (
    !confirm(
      `Delete "${name}"? This cannot be undone.`
    )
  ) {
    return;
  }


  try {

    await deleteProductRequest(id);

  } catch (err) {

    console.error(err);

    alert(
      'Could not delete the product. Please try again.'
    );

    return;
  }


  try {

    currentProducts =
      await getProducts(
        document.getElementById(
          'productSearch'
        )?.value || ''
      );

    renderProductRows(currentProducts);

  } catch (err) {

    console.error(err);

  }
}


/* =========================================================
   MAKE FUNCTIONS AVAILABLE TO HTML
   ========================================================= */

window.initDashboard = initDashboard;

window.initProductsPage = initProductsPage;

window.openModal = openModal;

window.closeModal = closeModal;

window.editProduct = editProduct;

window.deleteProduct = deleteProduct;


/* =========================================================
   OPTIONAL API TEST
   ========================================================= */

async function testAPIConnection() {

  try {

    const response =
      await fetch(API_ENDPOINTS.products);

    if (!response.ok) {
      throw new Error('API connection failed');
    }


    const data =
      await response.json();


    console.log(
      '✅ Products successfully loaded from MySQL through Flask:',
      data
    );


  } catch (error) {

    console.error(
      '❌ API Connection Error:',
      error
    );
  }
}


// Uncomment this only if you want
// to test the API manually.
//
// testAPIConnection();
// =========================================================
// AGRITRADE - GLOBAL DASHBOARD SEARCH
// Searches products from Flask + MySQL
// Clicking a product opens that specific product for editing
// =========================================================

const globalSearch = document.getElementById('globalSearch');

if (globalSearch) {

  // -------------------------------------------------------
  // Create search results dropdown
  // -------------------------------------------------------

  const searchResults = document.createElement('div');

  searchResults.id = 'globalSearchResults';

  searchResults.style.position = 'absolute';
  searchResults.style.top = 'calc(100% + 8px)';
  searchResults.style.left = '0';
  searchResults.style.right = '0';
  searchResults.style.background = '#ffffff';
  searchResults.style.border = '1px solid #e5ebe7';
  searchResults.style.borderRadius = '12px';
  searchResults.style.boxShadow = '0 8px 25px rgba(0,0,0,0.10)';
  searchResults.style.zIndex = '9999';
  searchResults.style.display = 'none';
  searchResults.style.maxHeight = '350px';
  searchResults.style.overflowY = 'auto';

  // -------------------------------------------------------
  // Get search container
  // -------------------------------------------------------

  const searchContainer = globalSearch.closest('.header-search');

  if (searchContainer) {
    searchContainer.style.position = 'relative';
    searchContainer.appendChild(searchResults);
  }

  let searchTimer = null;

  // -------------------------------------------------------
  // Search products while typing
  // -------------------------------------------------------

  globalSearch.addEventListener('input', function () {

    clearTimeout(searchTimer);

    const search = globalSearch.value.trim();

    // Nothing typed
    if (!search) {
      searchResults.style.display = 'none';
      searchResults.innerHTML = '';
      return;
    }

    // Wait 250ms before API request
    searchTimer = setTimeout(async function () {

      try {

        // ---------------------------------------------------
        // Get products from Flask API
        // ---------------------------------------------------

        const response = await fetch(
          `${API_ENDPOINTS.products}?search=${encodeURIComponent(search)}`
        );

        if (!response.ok) {
          throw new Error('Search failed');
        }

        const products = await response.json();

        // ---------------------------------------------------
        // No products found
        // ---------------------------------------------------

        if (!Array.isArray(products) || products.length === 0) {

          searchResults.innerHTML = `
            <div style="
              padding: 18px;
              text-align: center;
              color: #7a857e;
              font-size: 14px;
            ">
              No products found
            </div>
          `;

          searchResults.style.display = 'block';

          return;
        }

        // ---------------------------------------------------
        // Display products
        // ---------------------------------------------------

        searchResults.innerHTML = products.map(product => {

          return `
            <div
              class="global-search-item"
              data-id="${product.id}"
              style="
                padding: 14px 16px;
                border-bottom: 1px solid #edf1ed;
                cursor: pointer;
                transition: background 0.15s ease;
              "
            >

              <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
              ">

                <!-- Product information -->
                <div>

                  <strong style="
                    display: block;
                    color: #1f2a24;
                    font-size: 15px;
                    margin-bottom: 4px;
                  ">
                    ${escapeHtml(product.name)}
                  </strong>

                  <span style="
                    color: #7a857e;
                    font-size: 13px;
                  ">
                    ${escapeHtml(product.category)}
                    •
                    ${escapeHtml(product.variety)}
                  </span>

                </div>

                <!-- Stock information -->
                <div style="
                  text-align: right;
                  white-space: nowrap;
                ">

                  <strong style="
                    display: block;
                    color: #2f7d4a;
                    font-size: 14px;
                  ">
                    ${formatNumber(product.stock)}
                    ${escapeHtml(product.unit)}
                  </strong>

                  <span style="
                    color: #8a948d;
                    font-size: 12px;
                  ">
                    Stock
                  </span>

                </div>

              </div>

            </div>
          `;

        }).join('');

        searchResults.style.display = 'block';

        // ---------------------------------------------------
        // Add click + hover events
        // ---------------------------------------------------

        searchResults
          .querySelectorAll('.global-search-item')
          .forEach(item => {

            // Hover ON
            item.addEventListener('mouseenter', function () {

              item.style.background = '#f5f9f6';

            });

            // Hover OFF
            item.addEventListener('mouseleave', function () {

              item.style.background = '#ffffff';

            });

            // ------------------------------------------------
            // CLICK PRODUCT
            // ------------------------------------------------

            item.addEventListener('click', function () {

              const productId = item.dataset.id;

              console.log(
                'Selected product ID:',
                productId
              );

              // Put selected product name in search box
              globalSearch.value = item
                .querySelector('strong')
                .textContent
                .trim();

              // Hide search results
              searchResults.style.display = 'none';

              // ------------------------------------------------
              // Open Products page with selected product ID
              // ------------------------------------------------

              window.location.href =
                `products.html?edit=${encodeURIComponent(productId)}`;

            });

          });

      } catch (error) {

        console.error(
          'Global search error:',
          error
        );

        // -----------------------------------------------------
        // Show error
        // -----------------------------------------------------

        searchResults.innerHTML = `
          <div style="
            padding: 18px;
            color: #c0392b;
            font-size: 14px;
          ">
            Unable to search products
          </div>
        `;

        searchResults.style.display = 'block';

      }

    }, 250);

  });


  // =========================================================
  // Close dropdown when clicking outside
  // =========================================================

  document.addEventListener('click', function (event) {

    if (
      searchContainer &&
      !searchContainer.contains(event.target)
    ) {

      searchResults.style.display = 'none';

    }

  });


  // =========================================================
  // Close dropdown with ESC
  // =========================================================

  globalSearch.addEventListener('keydown', function (event) {

    if (event.key === 'Escape') {

      searchResults.style.display = 'none';

      globalSearch.blur();

    }

  });

}