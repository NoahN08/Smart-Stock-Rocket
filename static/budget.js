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

    sessionStorage.setItem("income-column", JSON.stringify(budgetData.income))
    sessionStorage.setItem("expenses-column", JSON.stringify(budgetData.expenses))
    sessionStorage.setItem("savings-column", JSON.stringify(budgetData.savings))

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

    const columnData = JSON.parse(sessionStorage.getItem(columnId))
    if (columnData != null) {
        columnData.forEach(entry => {
            addEntry(columnId, entry.descriptor, entry.value)
        })
    } else {
        // Add first entry-row in column
        addEntry(columnId)
    }

    calculateTotal(columnId)
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


function addEntry(columnId, defaultDesc="", defaultVal="") {
    const column = document.getElementById(columnId);
    const entriesContainer = column.querySelector(".entries");
    const newEntry = document.createElement("div");
    newEntry.classList.add("entry-row");
    newEntry.innerHTML = `
        <input type="text" class="descriptor" value="${defaultDesc}" placeholder="${inputPlaceholders[columnId]}">
        <input type="number" min="0" step="any" class="value" value="${defaultVal}" placeholder="Amount Per Month">
        <button type="button" class="delete-entry-row"> &#x2715; </button>
    `;

    entriesContainer.appendChild(newEntry);


    const descriptorInput = newEntry.querySelector(".descriptor");
    const valueInput = newEntry.querySelector(".value");

    // Update column total when value of one of the entries is changed
    valueInput.addEventListener("change", function() {
        calculateTotal(columnId);
    });

    // Focus event listeners
    descriptorInput.addEventListener("focus", function() {
        this.style.minWidth = "200px"; // Increase width on focus
    });
    valueInput.addEventListener("focus", function() {
        this.style.minWidth = "200px"; // Increase width on focus
    });

    // Blur event listeners
    descriptorInput.addEventListener("blur", function() {
        this.style.minWidth = ""; // Restore original width on blur
    });
    valueInput.addEventListener("blur", function() {
        this.style.minWidth = ""; // Restore original width on blur
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
    const loadingOverlay = document.getElementById('loading-overlay');
    const downloadButton = document.getElementById('download-pdf-button');
    loadingOverlay.style.display = 'flex'; // Show loading indicator

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
        loadingOverlay.style.display = 'none'; // Hide loading indicator
        downloadButton.style.display = 'block'; // Show download button
    })
    .catch((error) => {
        console.error('Error:', error);
        loadingOverlay.style.display = 'none'; // Hide loading indicator on error
        downloadButton.style.display = 'none'; // hide the download button, if it was somehow visible.
    });
}

// Add budget report to budget page
function displayBudget(budget_json) {
    budget = JSON.parse(budget_json)
    const budgetContainer = document.getElementById("budget-container");
    budgetContainer.innerHTML = '';

    // Create heading
    const heading = document.createElement("h3");
    heading.textContent = "Your Budget Report";
    budgetContainer.appendChild(heading);

    const chartContainer = document.createElement('div');
    chartContainer.id = 'chart-container';
    const incomeChartWrapper = document.createElement('div');
    const expenseChartWrapper = document.createElement('div');
    incomeChartWrapper.classList.add("chart-wrapper");
    expenseChartWrapper.classList.add("chart-wrapper");

    incomeChartCanvas = document.createElement('canvas');
    expenseChartCanvas = document.createElement('canvas');
    incomeChartCanvas.id = 'incomeChart';
    expenseChartCanvas.id = 'expenseChart';

    incomeChartWrapper.appendChild(incomeChartCanvas);
    expenseChartWrapper.appendChild(expenseChartCanvas);
    chartContainer.appendChild(incomeChartWrapper);
    chartContainer.appendChild(expenseChartWrapper);

    budgetContainer.appendChild(chartContainer);

    // Generate Chart.js charts
    generateIncomeChart(budget.ChartData.income_sources);
    generateExpenseChart(budget.ChartData.expense_categories);

    const tableData = budget.Table;
    const comments = budget.Comments.replace(/\n/g, '<br>');
    // Create the table
    const table = document.createElement('table');

    // Create the header row (keys)
    const headerRow = table.insertRow();
    for (const key in tableData) {
        const headerCell = headerRow.insertCell();
        headerCell.style.backgroundColor = "lightgray";
        headerCell.textContent = key;
    }

    // Create the data row (values)
    const dataRow = table.insertRow();
    for (const key in tableData) {
        const dataCell = dataRow.insertCell();
        dataCell.textContent = tableData[key];
    }

    // Display the comments
    const commentsHeading = document.createElement("h4");
    commentsHeading.textContent = "Our Recommendations";
    const commentsDiv = document.createElement('div');
    commentsDiv.innerHTML = comments;

    const detailedReport = budget.DetailedReportMarkdown

    // Append the table and comments to the page
    budgetContainer.appendChild(table);
    budgetContainer.append(commentsHeading)
    budgetContainer.appendChild(commentsDiv);
}

function generateIncomeChart(incomeData) {
    if (!incomeData || incomeData.length === 0) return; // Check for data

    const incomeLabels = incomeData.map(item => item.source);
    const incomeAmounts = incomeData.map(item => item.amount);

    const incomeColors = [
        '#3cb44b',
        '#aaffc3',
        '#fffac8',
        '#ffe119',
        '#ffd8b1',
        '#fabebe',
        '#e6beff',
        '#4363d8',
        '#46f0f0',
        '#ffffff'
    ];

    new Chart(document.getElementById('incomeChart'), {
        type: 'pie',
        data: {
            labels: incomeLabels,
            datasets: [{
                data: incomeAmounts,
                backgroundColor: incomeColors
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Income Sources',
                    font: {
                        size: 24
                    }
                }
            }
        }
    });
}

function generateExpenseChart(expenseData) {
    if (!expenseData || expenseData.length === 0) return; // Check for data

    const expenseLabels = expenseData.map(item => item.category);
    const expenseAmounts = expenseData.map(item => item.amount);

    const expenseColors = [
        '#4363d8',  // Blue - Utilities, Consistent
        '#46f0f0',  // Cyan - Transportation, Movement
        '#911eb4',  // Purple - Entertainment, Discretionary
        '#f58231',  // Orange - Food, Important (Moved)
        '#008080',  // Teal - Debt, Obligations
        '#e6194b',  // Red - Urgent, Important
        '#9a6324',  // Brown - Housing, Stable (Moved)
        '#f032e6',  // Magenta - Other, Miscellaneous
        '#000075',  // Navy - Insurance, Planning
        '#808080'   // Gray - Miscellaneous, Neutral
    ];

    new Chart(document.getElementById('expenseChart'), {
        type: 'pie',
        data: {
            labels: expenseLabels,
            datasets: [{
                label: 'Expenses',
                data: expenseAmounts,
                backgroundColor: expenseColors
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Expense Categories',
                    font: {
                        size: 24
                    }
                }
            }
        }
    });
}

const downloadButton = document.getElementById('download-pdf-button');
downloadButton.addEventListener('click', function() {
    downloadButton.disabled = true; // Disable the button
    fetch('/generate_budget_pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(budget) // Send the entire LLM response
    })
    .then(response => response.blob()) // Get the response as a blob
    .then(blob => {
        // Remove any existing download links
        const existingLink = document.querySelector('#download-link');
        if (existingLink) {
            existingLink.remove();
        }

        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'budget_report.pdf';
        a.id = 'download-link'; // Assign an ID for removal
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url); // Clean up

        downloadButton.disabled = false; // re-enable button.
    })
    .catch(error => {
        console.error('Error:', error);
        downloadButton.disabled = false; // re-enable button.
    });
});

const bankStatementUpload = document.getElementById('bankStatementUpload');
const uploadStatementButton = document.getElementById('uploadStatementButton');
const uploadStatus = document.getElementById('uploadStatus');
const budgetContainer = document.getElementById('budget-container');
const loadingOverlay = document.getElementById('loading-overlay');

uploadStatementButton.addEventListener('click', () => {
    const file = bankStatementUpload.files[0];
    if (file) {
        loadingOverlay.style.display = 'flex'; // Show loading

        const formData = new FormData();
        formData.append('bankStatement', file);

        fetch('/analyze_statement', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(llmResponse => {
            loadingOverlay.style.display = 'none'; // Hide loading
            // Process the LLM response to display the budget summary
            displayBudget(llmResponse);
            downloadButton.style.display = 'block'; // Show download button
            // Store the LLM response for PDF generation if needed later
            window.llmResponse = llmResponse;
        })
        .catch(error => {
            console.error('Error analyzing statement:', error);
            uploadStatus.textContent = 'Error during analysis.';
            loadingOverlay.style.display = 'none'; // Hide loading
        });
    } else {
        uploadStatus.textContent = 'Please select a file.';
    }
});

// Hide the download button initially
downloadButton.style.display = 'none';