# src/dashboard/app.R

library(shiny)
library(shinydashboard)
library(dplyr)
library(ggplot2)

# --- Standard configurations matching disease_profiles.py ---
diseases_list <- c(
  "Anthrax", "Foot and Mouth Disease", "Lumpy Skin Disease", 
  "Peste des Petits Ruminants", "Rift Valley Fever", "Trypanosomosis", 
  "Highly Pathogenic Avian Influenza", "Rabies", "Blackleg / Black Quarter"
)

# --- UI Layout Definition ---
ui <- dashboardPage(
  skin = "blue",
  dashboardHeader(title = "One Health Intelligence"),
  
  dashboardSidebar(
    sidebarMenu(
      id = "sidebar_tabs",
      menuItem("Disease Outbreak Analysis", tabName = "analysis", icon = icon("dashboard")),
      menuItem("Outbreak Report Status", tabName = "report_status", icon = icon("table"))
    ),
    
    # Conditional sidebar controls matching active tab selection
    conditionalPanel(
      condition = "input.sidebar_tabs == 'analysis'",
      selectInput("disease_select", "Select Disease:", choices = diseases_list, selected = "Anthrax"),
      selectInput("start_year", "Select Start Year:", choices = 2017:2026, selected = 2025),
      selectInput("end_year", "Select End Year:", choices = 2017:2026, selected = 2026),
      actionButton("submit_btn", "Apply Filters", class = "btn-primary", style = "margin-left: 15px; margin-top: 10px;")
    ),
    conditionalPanel(
      condition = "input.sidebar_tabs == 'report_status' && input.status_view == 'years'",
      h5("Select Reporting Year:", style = "margin-left: 15px; color: #b8c7ce; font-weight: bold;"),
      actionButton("year_2026_btn", "2026", class = "btn-warning", style = "width: 180px; margin-left: 15px; margin-bottom: 8px; font-weight: bold; color: black;"),
      actionButton("year_2025_btn", "2025", class = "btn-warning", style = "width: 180px; margin-left: 15px; margin-bottom: 8px; font-weight: bold; color: black;")
    )
  ),
  
  dashboardBody(
    tags$head(
      tags$style(HTML("
        .content-wrapper, .right-side { background-color: #f4f6f9; }
        .box.box-solid.box-primary > .box-header { background-color: #3c8dbc; }
        .box.box-solid.box-info > .box-header { background-color: #00c0ef; }
        .box.box-solid.box-danger > .box-header { background-color: #dd4b39; }
        .box.box-solid.box-warning > .box-header { background-color: #f39c12; }
        
        /* Outbreak Report Status styling */
        .status-header-box { background-color: #337ab7; color: white; padding: 15px; font-size: 24px; font-weight: bold; text-align: center; border-radius: 4px; margin-bottom: 20px; }
        .legend-tag { display: inline-block; padding: 6px 12px; margin-right: 10px; margin-bottom: 10px; border-radius: 4px; color: white; font-weight: bold; }
        .legend-green { background-color: #5cb85c; }
        .legend-yellow { background-color: #f0ad4e; }
        .legend-red { background-color: #d9534f; }
        .legend-blue { background-color: #337ab7; }
        
        /* Grid table alignment classes */
        .grid-cell { color: white; font-weight: bold; text-align: center; padding: 6px; border-radius: 2px; font-size: 11px; }
        .cell-green { background-color: #5cb85c; }
        .cell-yellow { background-color: #f0ad4e; }
        .cell-red { background-color: #d9534f; }
        .cell-blue { background-color: #337ab7; }
      "))
    ),
    
    # Hidden tracking state for nested views
    conditionalPanel(condition = "false", textInput("status_view", label = NULL, value = "years")),
    
    tabItems(
      # --- TAB 1: DISEASE OUTBREAK ANALYSIS ---
      tabItem(tabName = "analysis",
        fluidRow(
          valueBoxOutput("kpi_disease", width = 3),
          valueBoxOutput("kpi_outbreaks", width = 2),
          valueBoxOutput("kpi_attacks", width = 2),
          valueBoxOutput("kpi_susceptible", width = 3),
          valueBoxOutput("kpi_deaths", width = 2)
        ),
        fluidRow(
          box(title = "Regional Outbreaks and Attacks", width = 12, status = "warning", solidHeader = TRUE,
              plotOutput("outbreaks_bar_chart", height = "300px"))
        ),
        fluidRow(
          box(title = "Total Deaths by Region", width = 6, status = "danger", solidHeader = TRUE,
              plotOutput("deaths_pie_chart", height = "300px")),
          box(title = "Regional Results Summary", width = 6, status = "info", solidHeader = TRUE,
              tableOutput("district_results_table"))
        )
      ),
      
      # --- TAB 2: OUTBREAK REPORT STATUS ---
      tabItem(tabName = "report_status",
        conditionalPanel(
          condition = "input.status_view == 'years'",
          fluidRow(box(title = "Reporting Compliance Dashboard", width = 12, status = "warning", solidHeader = TRUE,
                       p("Select a target year on the left sidebar to view the monthly report upload status for all Ethiopian Regional States.")))
        ),
        conditionalPanel(
          condition = "input.status_view == 'grid'",
          fluidRow(
            column(12,
              div(class = "status-header-box", textOutput("grid_title_text")),
              actionButton("back_btn", "Back to Years", class = "btn-danger", style = "margin-bottom: 20px; font-weight: bold;"),
              div(style = "background-color: white; padding: 15px; border-radius: 4px; margin-bottom: 20px; border: 1px solid #ddd;",
                h4("Status Legend:", style = "font-weight: bold; margin-top: 0;"),
                span(class = "legend-tag legend-green", "Green: Data Received and Uploaded"),
                span(class = "legend-tag legend-yellow", "Yellow: Data Received and Not Uploaded"),
                span(class = "legend-tag legend-red", "Red: Data Not Received"),
                span(class = "legend-tag legend-blue", "Blue: Pending")
              ),
              box(width = 12, status = "primary", div(style = "overflow-x: auto;", htmlOutput("report_status_grid_html")))
            )
          )
        )
      )
    )
  )
)

# --- Server Logic Definition ---
server <- function(input, output, session) {
  
  # --- TAB CONTROL LOGIC ---
  selected_year_status <- reactiveVal(2026)
  observeEvent(input$year_2026_btn, { updateTextInput(session, "status_view", value = "grid"); selected_year_status(2026) })
  observeEvent(input$year_2025_btn, { updateTextInput(session, "status_view", value = "grid"); selected_year_status(2025) })
  observeEvent(input$back_btn, { updateTextInput(session, "status_view", value = "years") })
  
  output$grid_title_text <- renderText({ paste("Reporting Compliance Matrix -", selected_year_status()) })
  
  # --- TAB 1: DATA PROCESSING ---
  processed_data <- eventReactive(input$submit_btn, {
    filepath <- "../../data/processed/risk_assessment_output.csv"
    
    if (file.exists(filepath)) {
      raw_df <- read.csv(filepath, stringsAsFactors = FALSE)
    } else {
      # Fallback dummy data for initial load/testing
      raw_df <- data.frame(
        district = c("Jinka", "Asayita", "Yabelo", "Gode"),
        region = c("South_Ethiopia", "Afar", "Oromia", "Somali"),
        disease_name = c("Anthrax", "Anthrax", "Anthrax", "Anthrax"),
        active_cases = c(12, 18, 9, 3),
        population = c(45000, 68000, 89000, 54000),
        deaths = c(3, 5, 2, 0), year = c(2025, 2025, 2025, 2025)
      )
    }
    raw_df %>% filter(
      disease_name == input$disease_select,
      year >= as.numeric(input$start_year),
      year <= as.numeric(input$end_year)
    )
  }, ignoreNULL = FALSE)
  
  # --- KPI VALUE BOXES ---
  output$kpi_disease <- renderValueBox({ valueBox(input$disease_select, "Disease Profile", icon = icon("virus"), color = "green") })
  output$kpi_outbreaks <- renderValueBox({
    data <- processed_data()
    val <- if(nrow(data) > 0) sum(data$active_cases > 0) else 0
    valueBox(val, "Active Outbreaks", icon = icon("exclamation-triangle"), color = "orange")
  })
  output$kpi_attacks <- renderValueBox({
    data <- processed_data()
    val <- if(nrow(data) > 0) sum(data$active_cases) else 0
    valueBox(val, "Total Attacks", icon = icon("ambulance"), color = "blue")
  })
  output$kpi_susceptible <- renderValueBox({
    data <- processed_data()
    val <- if(nrow(data) > 0) sum(data$population) else 0
    valueBox(format(val, big.mark=","), "Total Susceptible", icon = icon("users"), color = "teal")
  })
  output$kpi_deaths <- renderValueBox({
    data <- processed_data()
    val <- if(nrow(data) > 0) sum(data$deaths) else 0
    valueBox(val, "Total Deaths", icon = icon("skull"), color = "red")
  })
  
  # --- CHARTS AND TABLES ---
  output$district_results_table <- renderTable({
    data <- processed_data()
    if (nrow(data) == 0) return(data.frame(Status = "No records found."))
    data %>% group_by(region) %>% summarise(Cases = sum(active_cases), Pop = sum(population)) %>%
      rename(Region = region, `Total Cases` = Cases, `Host Pop` = Pop)
  })
  
  output$outbreaks_bar_chart <- renderPlot({
    data <- processed_data()
    if (nrow(data) == 0) return(NULL)
    ggplot(data, aes(x = region, y = active_cases, fill = region)) + 
      geom_bar(stat = "identity") + theme_minimal() + labs(x = "Region", y = "Total Attacks") +
      theme(legend.position = "none")
  })
  
  output$deaths_pie_chart <- renderPlot({
    data <- processed_data()
    if (nrow(data) == 0 || sum(data$deaths) == 0) return(NULL)
    pie_data <- data %>% group_by(region) %>% summarise(Deaths = sum(deaths))
    ggplot(pie_data, aes(x = "", y = Deaths, fill = region)) + 
      geom_bar(stat = "identity", width = 1) + coord_polar("y", start = 0) + theme_void()
  })
  
  # --- COMPLIANCE GRID (DYNAMIC HTML) ---
  output$report_status_grid_html <- renderUI({
    regions <- c("South_Ethiopia", "Afar", "Somali", "Oromia", "Amhara", "Tigray", "Sidama", "Harari")
    months <- c("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    set.seed(selected_year_status())
    
    html <- "<table class='table table-bordered' style='background-color: white;'><thead><tr style='background-color: #f4f4f4;'><th>State Name</th>"
    for (m in months) html <- paste0(html, "<th style='text-align: center;'>", m, "</th>")
    html <- paste0(html, "</tr></thead><tbody>")
    
    for (r in regions) {
      html <- paste0(html, "<tr><td style='font-weight: bold;'>", r, "</td>")
      for (m in months) {
        rand <- runif(1)
        if (rand > 0.4) { class <- "cell-green"; txt <- "OK" }
        else if (rand > 0.2) { class <- "cell-yellow"; txt <- "Rec" }
        else if (rand > 0.1) { class <- "cell-red"; txt <- "Miss" }
        else { class <- "cell-blue"; txt <- "Pend" }
        html <- paste0(html, "<td><div class='grid-cell ", class, "'>", txt, "</div></td>")
      }
      html <- paste0(html, "</tr>")
    }
    HTML(paste0(html, "</tbody></table>"))
  })
}

# Run the Shiny application 
shinyApp(ui = ui, server = server)
