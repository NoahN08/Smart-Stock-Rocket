const budgetForm = document.getElementById("budget-form");
const columnIds = ["income-column", "expenses-column", "savings-column"];

const inputPlaceholders = {
    "income-column": "Income Source",
    "expenses-column": "Expense Category",
    "savings-column": "Savings Goal"
}

// setup the 3 input columns: income, expenses, savings goals
columnIds.forEach(columnId => {
    setupColumn(columnId);
});

// Handler for form submission
budgetForm.addEventListener("submit", function(event) {
    event.preventDefault();

    // Collect inputs from input columns
    const budgetData = {
      income: collectColumnData("income-column"),
      expenses: collectColumnData("expenses-column"),
      savings: collectColumnData("savings-column")
    };

    sendBudgetInfo(budgetData);
});

// function reused to set up each of the input columns
function setupColumn(columnId) {
    const column = document.getElementById(columnId);
    const entriesContainer = column.querySelector(".entries");
    const addEntryButton = column.querySelector(".add-entry-row");

    // Handler for "+" button to add new entry row
    addEntryButton.addEventListener("click", function() { addEntry(columnId) });

    // Handler for deleting entry rows
    entriesContainer.addEventListener("click", function(event) {
        if (event.target.classList.contains("delete-entry-row")) {
            columnId = this.parentElement.id
            event.target.parentElement.remove();
            calculateTotal(columnId);
        }
    });

    // Add first entry-row in column
    addEntry(columnId)
}

function collectColumnData(columnId) {
    const column = document.getElementById(columnId);
    const entries = column.querySelectorAll(".entry-row");
    const data = [];

    entries.forEach(entry => {
        const descriptor = entry.querySelector(".descriptor").value;
        const value = parseFloat(entry.querySelector(".value").value);
        data.push({ descriptor, value });
    });

    return data;
}


function addEntry(columnId) {
    const column = document.getElementById(columnId);
    const entriesContainer = column.querySelector(".entries");
    const newEntry = document.createElement("div");
    newEntry.classList.add("entry-row");
    newEntry.innerHTML = `
        <input type="text" class="descriptor" placeholder="${inputPlaceholders[columnId]}">
        <input type="number" class="value" placeholder="Amount Per Month">
        <button type="button" class="delete-entry-row"> &#x2715; </button>
    `;

    entriesContainer.appendChild(newEntry);


    const valueInput = newEntry.querySelector(".value");
    valueInput.addEventListener("change", function() {
        calculateTotal(columnId);
    });
};

function calculateTotal(columnId) {
    const column = document.getElementById(columnId);
    const entries = column.querySelectorAll(".entry-row");
    let total = 0;

    entries.forEach(entry => {
        const value = parseFloat(entry.querySelector(".value").value);
        if (!isNaN(value)) {
            total += value;
        }
    });

    column.querySelector(".total").textContent = `Total: $${total.toFixed(2)}`;
}

// Send budget info to generate_budget route
function sendBudgetInfo(budgetData) {

    // Call API route to generate budget
    fetch('/generate_budget', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(budgetData),
    })
    .then(response => response.json())
    .then(data => {
        displayBudget(data.response);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Add budget report to budget page
function displayBudget(budget_json) {
    budget = JSON.parse(budget_json)
    const budgetContainer = document.getElementById("budget-container");

    // Create heading
    const heading = document.createElement("h3");
    heading.textContent = "Your Budget Report";

    // Generate table with number outputs
    const tableElement = document.createElement("table");
    const tableBody = document.createElement("tbody")
    const tableHeaderRow = document.createElement("tr");
    const tableValueRow = document.createElement("tr");
    Object.entries(budget.Table).forEach(([key, value]) => {
        const header = document.createElement("th");
        header.appendChild(document.createTextNode(key));
        tableHeaderRow.appendChild(header);
        const cell = document.createElement("td");
        cell.appendChild(document.createTextNode(value));
        tableValueRow.appendChild(cell);
    });
    tableBody.appendChild(tableHeaderRow);
    tableBody.appendChild(tableValueRow);
    tableElement.appendChild(tableBody);
    tableElement.classList.add("table")

    // Create div to hold general comments/suggestions from AI
    const commentsElement = document.createElement("div");
    commentsElement.textContent = budget.Comments;

    // Clear budgetContainer and add new elements
    budgetContainer.innerHTML = '';
    budgetContainer.appendChild(heading);
    budgetContainer.appendChild(tableElement);
    budgetContainer.appendChild(commentsElement);
    budgetContainer.scrollTop = budgetContainer.scrollHeight;
}