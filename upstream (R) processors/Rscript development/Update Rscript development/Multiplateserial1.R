library(dplyr)
library(rlist)
library(readxl)
library(readr)

#Get the filename and parse it into seperate parts
main<- read_xlsx(file_path, file_name="")
stockList <- tryCatch({
  GetStockList(file_path)
},
error = function(cond){
  if(errMessage == ""){
    errMessage <<- "Input file error - stockList"
  }
  return(NA)
})

#get the drug concentrations(stocklist)
GetStocklist <- function(file_name){
  stocks<<-read_xlsx(file_name)
}





# #TROUBLESHOOTING---------
errMessage <<- ""
fpath <- "C:\\Users\\jornb\\OneDrive\\Work\\Maik"
dataName <- "MV_InputTemplate.xlsx"
dqs <- main(paste(fpath, dataName, sep="//"))