library(shiny)

shinyUI(
  pageWithSidebar(
    headerPanel("Multiplate MIC singlechannel pipette function- OT2 Commander"),
    
    sidebarPanel(
      #link to home
      actionButton("Home", "Home", width='300px',
                   onclick ="window.open('https://vanhasseltlab.lacdr.leidenuniv.nl/ot2/home')"),
      actionButton("Multichannel", "Multichannel", width = '300px',
                   onclick="C:\\Users\\jornb\\Desktop\\ot2-main\\MVPlate MCP\\multichannel\\ui"),
      
      #main
      fileInput("file", "Upload Plate Map", accept=".xlsx"),
      downloadButton("downloadTemplate", label = "Template Input"),
      textInput("pmid", 'Plate Map ID (PMID)'),
      textInput("f_name", 'First Name'),
      textInput("l_name", 'Last Name'),
      textInput("exp_name", 'Experiment Name'),
      textInput("exp_num", 'Experiment Number'),
      textOutput('tex'),
      actionButton("do", "Confirm uploaded file and save"),
      uiOutput('downloadData'),
      uiOutput('downloadData2')
    ),
    mainPanel(
      tableOutput('tab')
    )
))