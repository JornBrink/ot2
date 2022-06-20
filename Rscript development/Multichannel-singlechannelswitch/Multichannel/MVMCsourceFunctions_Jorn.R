####################################################
# stil to do meta:
# 1. make it function at all  - right now it gets most variables that it  needs but still needs to:
#                             - parse into vectors
#                             - solvent list
#                             - Dilution calcualtion
#                             - Dilution map
#                             - make the command list
#                             - have excess
#                             - Load the decklist map
#                             - create the actual list of commands
#                             - Make a good output
# 2. clean it up with the function() tools
# 3. annotate everything
# 4. let is speak with the server (not looking forward to this)
# a good thing to do is to first seperate the functions and then recombine them in this 
####################################################

library(shiny)
library(readxl)
library(writexl)
library(dplyr)

options(stringsAsFactors = F)
file_name <- read_xlsx(file.choose())

#subsetting antibiotic stock
Stocksolutions<-file_name[c(1), 3:10]                                    #subsetting the first two rows note:right now you can have max 8 antibiotic conc here
Stocksolutions<-Stocksolutions[ , colSums(is.na(Stocksolutions)) == 0]  #removing the columns with one NA in it

#subsetting getting the final volume and inoculum
Fvol<-file_name[c(4), 3]
Ivol<-file_name[c(5), 3]

#number of plates needed
Nplates<-file_name[c(5), 6]

#get reservoir use
Reservoir<-file_name[c(5), 8]

#platemap finished look at seperate file

#preparation --> solmap dillution and the dilution map