library(shiny)
shinyUI(
    pageWithSidebar(
        headerPanel("Output Preprocessor for 96-Well Plate"),
        
        sidebarPanel(
            #link to home
            actionButton("Home", "Home", width='300px',
                         onclick ="window.open('https://ot2.lacdr.leidenuniv.nl/ot2/home')"),
            
            #file inputs
            fileInput("files", "Upload Measurement Data", accept=".csv",
                      multiple=T),
            fileInput("pMap", "Upload Plate Map", accept=".xlsx"),
            
            #control selection
            uiOutput("ctrlSelectionUI"),
            checkboxInput("separate_control", "Separate control plate", value=F),
            uiOutput("control_meas_upload"),
            uiOutput("control_map_upload"),
            uiOutput("coord_map_download"),
            
            
            #names
            textInput("folderName", "Experiment Name", value='defaultFolder'),
            
            #action buttons
            actionButton("do", "Confirm uploaded file and save", width=300),
            
            #downloadButton("downloadScript", "Download Processor Script", width=300),
            
            #downloads
            uiOutput('download_prcNM'),
            uiOutput('download_controlNM')
        ),
        
        mainPanel(
            textOutput('err_message'),
            tableOutput('tab')
        )
))
