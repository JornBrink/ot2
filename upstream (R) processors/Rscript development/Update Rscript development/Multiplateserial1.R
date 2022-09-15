library(dplyr)
library(rlist)
library(readxl)
library(readr)
#testing purposes
Filename <- "C:\\Users\\jornb\\OneDrive\\Work\\Maik\\MV_InputTemplate.xlsx"

#Get the filename and parse it into seperate parts
main<- read_xlsx(Filename)

#stocklist First
stocklist<-read_xlsx(Filename, range="C1:M2") %>% data.frame() %>%
  select_if(function(x) any(!is.na(x)))
sl_res<- unlist(stocklist)
if(is.character(sl_res[1])){
  sl_res <- gsub(",", ".", sl_res) %>% as.numeric()
}

names(sl_res) <- colnames(stocklist)

#Get the well volume
Wellvol <- read_xlsx(Filename, range = "C5:C6", col_names=F)%>% unlist()
names(Wellvol) <- c("TotalVol", "FillVol")

#Amount of wellplate
Wellpnum<- read_xlsx(Filename, range = "F6", col_names=F)%>% unlist()

#Full plate map
rawplatemap <- read_xlsx(Filename, range ="B57:M64", col_names=F)%>% data.frame()
rownames(rawplatemap) <- LETTERS[1:8]
colnames(rawplatemap) <- sapply(c(1:12), toString)

#make to vector
map <- c()
for(row in c(1:8)){
  curRow <- unlist(rawplatemap[row,])
  well_id<- sapply(c(1:12), function(x) paste(LETTERS[row], toString(x), sep=''))
  curRow <- cbind(well_id, curRow)
  map <- rbind(map, curRow)
}


#parse names
finmap <- c()
parsed_names <- sapply(map[,2], function(x) strsplit(x, ' ', fixed=T))

for(i in c(1:length(parsed_names))){
  #if well is empty
  if(map[i,2]!="0" & map[i,2]!=""){
    if(parsed_names[[i]][1]=="0"){
      #if both drug name and inoculum is not filled, then it is a blank fill well (which might as well be blank control)
      next_info <- c("FILL",
                    "NA",                 #drug name
                    parsed_names[[i]][1], #concentration
                    parsed_names[[i]][2], #solvent
                    "NA")                 #inoculum
    }else{
      #if all info is complete OR inoculum not added
      next_info <- c(paste(parsed_names[[i]][1], parsed_names[[i]][2], parsed_names[[i]][3], sep=' '),
                    parsed_names[[i]][1], #drug name
                    parsed_names[[i]][2], #concentration
                    parsed_names[[i]][3], #solvent
                    parsed_names[[i]][4]) #inoculum
    }
    #concatenate well
    finmap <- rbind(finmap, next_info)
    rownames(finmap) <- c()
  }
}

#remove blanks for the map
map <- map[(map[,2]!=""),]
map <- map[(map[,2]!="0"),]

#concatenate info
finmap <- cbind.data.frame(map, finmap)
colnames(finmap) <- c('Well', 'fillID', 'solID', 'DrugType','DrugConc', 'Solvent', 'Inoc')
finmap$Inoc[is.na(finmap$Inoc)] <- "NA"

if(is.character(finmap$DrugConc[1])){
  finmap$DrugConc <- gsub(",", ".", finmap$DrugConc) %>% as.numeric()
}

finmap[] <- lapply(finmap, as.character)
