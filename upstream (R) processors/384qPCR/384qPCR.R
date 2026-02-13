#LIBRARIES--------
options(stringsAsFactors = F)
library(dplyr)
library(rlist)
library(readxl)
library(tidyr)

#Functions---------
# Function: split_larger_rows
# Splits rows where the total volume exceeds a threshold
#helper functions----------------
split_larger_rows <- function(df, max_volume = 2000) {
  
  volume_cols <- c("Sensimix", "FWprimer", "RVprimer",
                   "buffer", "MgCl2", "H2O")
  
  i <- 1
  while (i <= nrow(df)) {
    
    if (df$totalvol[i] > max_volume) {
      
      # halve only volumes
      df[i, volume_cols] <- df[i, volume_cols] / 2
      df$totalvol[i] <- sum(df[i, volume_cols])
      
      # duplicate row
      new_row <- df[i, ]
      rownames(new_row) <- paste0(rownames(new_row), "_splitted")
      new_row$totalvol <- sum(new_row[volume_cols])
      df <- rbind(df, new_row)
      
    } else {
      i <- i + 1
    }
  }
  
  return(df)
}

get_last_position <- function(df) {
  idx <- max(which(!is.na(df$Slot_Id)))
  df[idx, c("Deck_Id", "Slot_Id")]
}

fill_positions <- function(df, start_deck, start_slot, slots) {
  n <- nrow(df)
  out_slots <- character(n)
  out_decks <- integer(n)
  
  start_idx <- match(start_slot, slots)
  if (is.na(start_idx)) stop("Invalid start_slot")
  
  linear_start <- (start_deck - 1) * length(slots) + start_idx
  linear_seq <- linear_start + seq_len(n)
  
  out_decks <- ((linear_seq - 1) %/% length(slots)) + 1
  out_slots <- slots[((linear_seq - 1) %% length(slots)) + 1]
  
  df$Deck_Id <- out_decks
  df$Slot_Id <- out_slots
  df
}

expand_primers_for_mastermixes <- function(primer_info, mastermix_names) {
  stopifnot(length(mastermix_names) %% 1 == 0)
  
  base_mm <- unique(sub("_splitted$", "", mastermix_names))
  
  expanded <- lapply(mastermix_names, function(mm) {
    base_name <- sub("_splitted$", "", mm)
    idx <- which(base_mm == base_name)
    
    rows <- primer_info[(2 * idx - 1):(2 * idx), , drop = FALSE]
    rows$Mastermix <- mm
    rows
  })
  
  result <- do.call(rbind, expanded)
  
  stopifnot(
    nrow(result) == 2 * length(mastermix_names),
    all(table(result$Mastermix) == 2)
  )
  
  rownames(result) <- NULL
  result
}

#big functions --------------
GetPlateMap <- function(file_name){
  res <- read_xlsx(file_name, 1, range= "B42:Y57", col_names= F)%>% data.frame()
  rownames(res) <- LETTERS[1:16] # rownames A-P
  colnames(res) <- sapply(c(1:24), toString) #Plate columns 1-24
  
  #Vectormap
  map <- c()
  for(row in c(1:16)){
    #sub-setting
    curRow <- unlist(res[row,])
    #get the info
    well_id <- sapply(c(1:24), function(x) paste(LETTERS[row], toString(x), sep= ' '))
    curRow <- cbind(well_id, curRow)
    map <- rbind(map,curRow)
  }
  fin_map <- c()
  parsed_names <- sapply(map[,2], function(x) strsplit(x, ' ', fixed = T))
  
  Filtered_genes <- lapply(parsed_names, function(x){
    if (length(x) >= 2){
      x[2]
    }else {
      NA
    }
  })
  
  Filtered_names <- lapply(parsed_names, function(x){
    if(length(x) >= 1){
      x[1]
    }else{
      NA
    }
  })

  res3 <- as.data.frame(do.call(rbind, Filtered_names))
  res3$V2 <- Filtered_genes
  res3$well_name <- sapply(LETTERS[1:16], function(x) paste0(x, c(1:24))) %>% as.vector()
  rownames(res3) <- res3[,3]
  res3$well_name <- NULL
  colnames(res3) <- c("Sample_name", "Gene_name")
  map <- res3
  return(map)
}

GetreactionNum <- function(file_name){
  res <- read_xlsx(file_name, 1, range= "B42:Y57", col_names= F)%>% data.frame()
  rownames(res) <- LETTERS[1:16] # rownames A-P
  colnames(res) <- sapply(c(1:24), toString) #Plate columns 1-24
  
  #Vector
  map <- c()
  for(row in c(1:16)){
    #sub-setting
    curRow <- unlist(res[row,])
    #get info
    well_id <- sapply(c(1:24), function(x) paste(LETTERS[row], toString(x), sep=''))
    curRow <- cbind(well_id, curRow)
    map <- rbind(map, curRow)
  }
  
  #parsing names
  fin_map <- c()
  parsed_names <- sapply(map[,2], function(x) strsplit(x, ' ', fixed=T))
  
  
  parsed_names <- parsed_names[!is.na(parsed_names)]
  
  #filtering the primers out of it
  Filtered_genes <- lapply(parsed_names, function(x) {
    if (length(x) >= 2) { # Check if the element has at least two values
      x[2]  # No explicit return, R automatically returns the last expression
    } else {
      NA    # This is the last expression if the condition is false
    }
  })
  res2 <- unlist(Filtered_genes)
  
  # Create a data frame with the original order of genes
  gene_list <- data.frame(Gene = res2, stringsAsFactors = FALSE)
  
  # Count the occurrences of each gene while preserving their original order
  gene_list$Count <- ave(seq_along(gene_list$Gene), gene_list$Gene, FUN = length)
  
  # Remove duplicates, keeping only the first appearance of each gene
  gene_list <- gene_list[!duplicated(gene_list$Gene), ]
  
  # Set row names and return the data frame
  rownames(gene_list) <- gene_list$Gene
  
  gene_list$Gene <- NULL
  
  return(gene_list)
}

MMscheme <- function(R_num){
  #first parameters Mastermix
  sensi <- 1.5
  FW <- 0.36
  RV <- 0.36
  Buff <- 0.5
  MgCl2 <- 0.36
  H2O <- 2.92
  
  mastermix <- R_num
  mastermix$ExcessReactions <- mastermix$Count + 15
  mastermix$Sensimix <- mastermix$ExcessReactions * sensi
  mastermix$FWprimer <- mastermix$ExcessReactions * FW
  mastermix$RVprimer <- mastermix$ExcessReactions * RV
  mastermix$buffer <- mastermix$ExcessReactions * Buff
  mastermix$MgCl2 <- mastermix$ExcessReactions * MgCl2
  mastermix$H2O <- mastermix$ExcessReactions * H2O
  mastermix$Count <- NULL
  mastermix$ExcessReactions <- NULL
  mastermix$totalvol <- rowSums(mastermix)
  
  # Rename rows and handle volume exceeding threshold
  rownames(mastermix) <- paste("Mastermix", seq_len(nrow(mastermix)))
  mastermix$Gene <- rownames(mastermix)
  allmix <- split_larger_rows(mastermix)
  allmix$totalvol <- NULL
  
  return (allmix)
}

#Sollist
SolList_fill <- function(mastermix){

  #time to generate the volume of the needed items
  sensimixvol <- sum(mastermix$Sensimix)
  buffervol <- sum(mastermix$buffer)
  MgCl2vol <- sum(mastermix$MgCl2)
  H2Ovol <- sum(mastermix$H2O)
  track <- 0
  if(H2Ovol > 2000){
    H2Ovol <- H2Ovol/2
    H2Ovol <- data.frame(H2Ovol)
    H2Ovol <- rbind(H2Ovol, H2Ovol)
    rownames(H2Ovol) <- paste("H2O", seq_len(nrow(H2Ovol)))
    colnames(H2Ovol) <- c("ul")
    track <- 1
  }
  
  #firs aggregrate primers if they are for the same type of mmx
  res <- data.frame(mastermix$FWprimer, mastermix$Gene)
  colnames(res) <- c("ul","gene")
  
  #group by gene (mmx) then rearrage that mmx 1 is top and next is mmx 2
  res <- res %>% group_by(gene) %>%
    summarise(
      ul = sum(ul, na.rm = TRUE),
      .groups = "drop"
    )
  
  #and rearranging so that 10 is not earlier then 2
  res <- res %>%   mutate(mm_num = as.numeric(sub(".*?(\\d+)$", "\\1", gene))) %>%
    arrange(mm_num) %>%
    select(-mm_num)
  
  #now to recall it and make it about the primers
  
  FWprimer <- data.frame(res$ul)
  rownames(FWprimer) <- paste("Forward primer", seq_len(nrow(FWprimer)))
  colnames(FWprimer) <- c("ul")
  FWprimer[1] <- FWprimer[1] + 100
  for (i in seq_len(nrow(FWprimer))){
    if(FWprimer$ul[i] > 200){
      FWprimer$ul[i] <- 200
    }
  }
  
  Rvprimer <- data.frame(res$ul)
  rownames(Rvprimer) <- paste("Reverse primer", seq_len(nrow(Rvprimer)))
  colnames(Rvprimer) <- c("ul")
  Rvprimer[1] <- Rvprimer[1] + 100
  for (i in seq_len(nrow(Rvprimer))){
    if(Rvprimer$ul[i] > 200){
      Rvprimer$ul[i] <- 200
    }
  }
  
  #complete the vollist to sollist for later assignment
  vollist <- rbind(sensimixvol,buffervol,MgCl2vol,H2Ovol)
  SolList <- data.frame(vollist)
  colnames(SolList) <- c("ul")
  
  if(track == 1){
    rownames(SolList) <- c("sensimixvol", "buffervol", "MgCl2vol", rownames(H2Ovol))
  }
  
  colnames(SolList) <- c("ul")
  
  SolList[1] <- SolList[1] + 100 #100 ul excess
  SolList <- rbind(SolList, FWprimer, Rvprimer)
  
  #add location in eppy
  rows <- LETTERS[1:4]  # Rows A-D
  cols <- 1:6           # Columns 1-6
  slots <- c()
  for (row in rows) {
    slots <- c(slots, paste0(row, cols))
  }
  
  #formatting SolList for future Solution List
  SolList$Slot_Id <- slots[seq_len(nrow(SolList))]
  SolList$Deck_Id <- 5
  SolList <- SolList %>% select(Slot_Id, everything())
  SolList <- SolList %>% select(Deck_Id, everything())
  na_index <- which(is.na(SolList$Slot_Id))
  
  if (length(na_index) > 0){
    SolList$Deck_Id[na_index:length(SolList$Deck_Id)] <- 5
    reset_slots <- slots[seq_len(nrow(SolList) - na_index[1]+1)]
    SolList$Slot_Id[na_index:nrow(SolList)] <- reset_slots[seq_along(na_index:nrow(SolList))]
  }
  
  return(SolList)
}

Samplecoll <- function(file_name){
  res <- read_xlsx(file_name, 1, range= "B42:Y57", col_names= F)%>% data.frame()
  rownames(res) <- LETTERS[1:16] # rownames A-P
  colnames(res) <- sapply(c(1:24), toString) #Plate columns 1-24
  
  #Vector
  map <- c()
  for(row in c(1:16)){
    #sub-setting
    curRow <- unlist(res[row,])
    #get info
    well_id <- sapply(c(1:24), function(x) paste(LETTERS[row], toString(x), sep=''))
    curRow <- cbind(well_id, curRow)
    map <- rbind(map, curRow)
  }
  
  #parsing names
  fin_map <- c()
  parsed_names <- sapply(map[,2], function(x) strsplit(x, ' ', fixed=T))
  parsed_names <- parsed_names[!is.na(parsed_names)]
  
  #filtering the primers out of it
  Filtered_genes <- lapply(parsed_names, function(x) {
    if (length(x) >= 2) { # Check if the element has at least two values
      x[1]  # No explicit return, R automatically returns the last expression
    } else {
      NA    # This is the last expression if the condition is false
    }
  })
  res2 <- unlist(Filtered_genes)
  
  # Create a data frame with the original order of genes
  gene_list <- data.frame(Gene = res2, stringsAsFactors = FALSE)
  
  # Count the occurrences of each gene while preserving their original order
  gene_list$Count <- ave(seq_along(gene_list$Gene), gene_list$Gene, FUN = length)
  
  # Remove duplicates, keeping only the first appearance of each gene
  gene_list <- gene_list[!duplicated(gene_list$Gene), ]
  
  # Set row names and return the data frame
  rownames(gene_list) <- gene_list$Gene
  
  gene_list$Gene <- NULL
  
  # rows <- LETTERS[1:4]  # Rows A-D
  # cols <- 1:6           # Columns 1-6
  # slots <- c()
  # for (row in rows) {
  #   slots <- c(slots, paste0(row, cols))
  # }
  # 
  # gene_list <- data.frame(gene_list)
  # gene_list$Deck_Id <- 9
  # gene_list$Slot_Id <- slots[seq_len(nrow(gene_list))]
  # 
  # na_index <- which(is.na(gene_list$Slot_Id))
  # 
  # if (length(na_index) > 0) {
  #   # Update Deck_Id starting from the first NA
  #   gene_list$Deck_Id[na_index:length(gene_list$Deck_Id)] <- 10
  #   
  #   # Reset Slot_Id starting from A1
  #   reset_slots <- slots[seq_len(nrow(gene_list) - na_index[1] + 1)]
  #   gene_list$Slot_Id[na_index:nrow(gene_list)] <- reset_slots[seq_along(na_index:nrow(gene_list))]
  # }
  # 
  # #moving the slotid to front (easier read)
  # gene_list <- gene_list %>% select(Slot_Id, everything())
  # gene_list <- gene_list %>% select(Deck_Id, everything())
  # gene_list$Count <- NULL
  return(gene_list)
}

#Commandlist functions ------------
cmd_mmprep <- function(SolList, Mastermix) {
  
  # --- Strip volumes from SolList (used later for commands)
  Amountsollist <- SolList$ul
  SolList$ul <- NULL
  
  # --- Identify primer rows
  primer_pattern <- grepl("Forward primer \\d+|Reverse primer \\d+", rownames(SolList))
  primerres <- SolList[primer_pattern, ]
  SolList <- SolList[!primer_pattern, ]
                    
  rownames(SolList) <- c("Sensimix", "buffer", "MgCl2", "H2O")
  
  # --- Build mastermix preparation commands (unchanged logic)
  cmd_start <- c()
  cur_asp <- 1
  cur_tip <- 1
  mix <- 0
  
  for (i in seq_len(nrow(SolList))) {
    curset <- SolList[i, ]
    cursol <- cbind(Mastermix[1], Mastermix[2], Mastermix[row.names(curset)])
    
    for (j in seq_len(nrow(cursol))) {
      commentvariable <- colnames(cursol[j,])
      commentvariable <- commentvariable[!commentvariable %in% c("Deck_Id", "Slot_Id")]
      cmd_cur <- bind_cols(
        curset,
        cursol[j,],
        mix,
        cur_tip,
        cur_asp,
        "NVT",
        paste("Putting", commentvariable, "into mix")
      )
      colnames(cmd_cur) <- c(
        "from_deck", "from_slot",
        "to_deck", "to_slot",
        "amt", "mix", "tip_n", "asp_set", "pipette", "comment"
      )
      cmd_start <- rbind(cmd_start, cmd_cur)
    }
    cur_asp <- cur_asp + 1
    cur_tip <- cur_tip + 1
  }
  
  # --- Primer locations (base primers only)
  primer_names <- rownames(primerres)
  primer_info <- data.frame(
    PrimerType = ifelse(grepl("Forward", primer_names), "FWprimer", "RVprimer"),
    Deck_ID_Primer = primerres$Deck_Id,
    Slot_ID_Primer = primerres$Slot_Id,
    stringsAsFactors = FALSE
  )
  # --- Expand primers to include `_splitted` mastermixes
  primer_info <- expand_primers_for_mastermixes(
    primer_info = primer_info,
    mastermix_names = rownames(Mastermix)
  )
  
  # --- Primer volumes per mastermix
  volmm <- data.frame(
    FWprimer = Mastermix$FWprimer,
    RVprimer = Mastermix$RVprimer,
    row.names = rownames(Mastermix),
    check.names = FALSE
  )
  
  volume_long <- volmm %>%
    pivot_longer(
      cols = everything(),
      names_to = "PrimerType",
      values_to = "Volume"
    ) %>%
    mutate(
      Mastermix = rep(rownames(volmm), each = ncol(volmm))
    )
  
  # --- Identity-safe merge
  combined <- merge(
    primer_info,
    volume_long,
    by = c("PrimerType", "Mastermix"),
    sort = FALSE
  )
  
  stopifnot(
    nrow(combined) == 2 * nrow(Mastermix),
    all(table(combined$Mastermix) == 2)
  )
  
  # --- Add mastermix destination locations
  combined <- merge(
    combined,
    Mastermix[, c("Deck_Id", "Slot_Id")],
    by.x = "Mastermix",
    by.y = "row.names"
  )
  
  final_primertable <- data.frame(
    from_deck = combined$Deck_ID_Primer,
    from_slot = combined$Slot_ID_Primer,
    to_deck   = combined$Deck_Id,
    to_slot   = combined$Slot_Id,
    amt       = combined$Volume
  )
  
  # --- Generate primer pipetting commands
  cmd_primer <- c()
  
  for (j in seq_len(nrow(final_primertable))) {
    cmd_cur <- bind_cols(
      final_primertable[j, ],
      mix = 0,
      tip_n = cur_tip,
      asp_set = cur_asp,
      pipette = "NVT",
      comment = "Adding primers to mastermix"
    )
    colnames(cmd_cur) <- c(
      "from_deck", "from_slot",
      "to_deck", "to_slot",
      "amt", "mix", "tip_n", "asp_set", "pipette", "comment"
    )
    cmd_primer <- rbind(cmd_primer, cmd_cur)
    cur_asp <- cur_asp + 1
    cur_tip <- cur_tip + 1
  }
  
  rbind(cmd_start, cmd_primer)
}

cmd_plate <- function(mastermix, platemap, cmd_listmm){
  #first get all the volume in each tube.
  allvolmmx <-mastermix[3:8]
  allvolmmx$totalvol <- rowSums(allvolmmx)
  totalvol <- allvolmmx[7]
  totalvol$Mastermix <- rownames(totalvol)
  
  #for this part only location is interesting
  locmm <- mastermix[1:2]
  
  #omit nas from the plate map
  platemap <- platemap[!(is.na(platemap$Gene_name)),]

  #make positions a column and remove sample name
  platemap$slot <- rownames(platemap)
  platemap$Sample_name<- NULL
  
  #Convert factor columns to characters
  platemap[] <- lapply(platemap, function(col){
    if (is.factor(col)) as.character(col) else col
  })
  
  #get the unique genenames
  unique_genes <- unique(platemap$Gene_name)
  
  # Assign Mastermix labels to each unique Gene_name
  mastermix_map <- setNames(paste0("Mastermix ", seq_along(unique_genes)), unique_genes)
  
  # Map Mastermix labels back to the original plate_map
  platemap$Mastermix <- sapply(platemap$Gene_name, function(gene) mastermix_map[[gene]])
  
  #assign mastermix lablels to each Gene name
  mastermix_map <- setNames(paste0("Mastermix ", seq_along(unique_genes)), unique_genes)
  
  locmm$Mastermix <- rownames(locmm)

  #define reactionvolume and leftover volume
  Rvol <- 6
  LRvol <- 30
  
  df <- platemap %>%
    left_join(totalvol, by = "Mastermix") %>%
    group_by(Mastermix) %>%
    mutate(
      rxn_index = row_number(),
      used_volume = rxn_index * Rvol,
      remaining_volume = totalvol - used_volume,
      needs_split = remaining_volume < LRvol
    ) %>%
    ungroup() %>%
    mutate(
      Mastermix = if_else(
        needs_split,
        paste0(Mastermix, "_splitted"),
        Mastermix
      )
    ) %>%
    select(-rxn_index, -used_volume, -remaining_volume, -needs_split)
  
  
  #combining the two
  combined <- merge(df, locmm, by = c("Mastermix"))
  
  #removing the totalvol for combined
  combined <- combined %>% 
    select(-totalvol)
  
  #add location to the plate
  combined$decklocplate <- 2
  combined <- combined[order(as.numeric(sub("Mastermix ", "", combined$Mastermix))), ]
  
  tip_n <- tail(cmd_listmm$tip_n, n=1)
  asp_set <- tail(cmd_listmm$asp_set, n=1)
  
  #amount to asp
  amt <- 6
  
  #make ready the cmd itself
  res <- data.frame(
    from_deck <- combined$Deck_Id,
    from_slot <- combined$Slot_Id,
    to_deck <- combined$decklocplate,
    to_slot <- combined$slot,
    amt <- amt
  )

  # putting the columns correct
  colnames(res) <- c("from_deck", "from_slot", "to_deck", "to_slot", "amt")
  tip_n <- tip_n + 1
  asp_set<-asp_set + 1
  
  #get the data frame ready
  cmdplating <- cmd_listmm
  
  #volume counter to prevent p1000 use aka p50 values
  camtmin <- 40
  camtmax <- 50
  
  #adding n_tip and asp_set
  for(i in 1:nrow(res)){
    cur <- res[i,]
    min <- res[i-1,]
    
    if(i != 1){
      if(cur$from_slot != min$from_slot & i != 1){
        camt = amt
        mix <- 2
        tip_n <- tip_n + 1
        asp_set <- asp_set + 1
        res2 <- res[i,]
        pipette <- "NVT"
        comment <- "Plating Mastermix to plate"
        res2 <- cbind(res2, mix, tip_n, asp_set, pipette, comment)
        cmdplating <- rbind(cmdplating, res2)
      }else{
        res2 <- res[i,]
        pipette <- "NVT"
        comment <- "Plating Mastermix to plate"
        camt <- camt + amt
        mix <- 1
        if (between(camt, camtmin, camtmax)){
          asp_set <- asp_set + 1
          camt = amt
        }else{
          print("")
        }
        res2 <- cbind(res2, mix, tip_n, asp_set, pipette, comment)
        cmdplating <- rbind(cmdplating, res2)
      }
      
    }else{
      res2 <- res[i,]
      mix <- 2
      pipette <- "NVT"
      comment <- "Plating Mastermix to plate"
      camt <- amt
      res2 <- cbind(res2, mix, tip_n, asp_set, pipette, comment)
      cmdplating <- rbind(cmdplating, res2)
    }
  }
  
  rownames(cmdplating) <- NULL
  cmdplating <- cmdplating[order(cmdplating$asp_set), ]
  return(cmdplating)
}

cmd_sample <- function(sampledeck, platemap, cmd_listp){
  #Function to finish the entire sample cmd.
  #First get the loc of the samples
  locsamp <- sampledeck[2:3]
  
  #omit nas
  platemap <- platemap[!(is.na(platemap$Sample_name)),]
  
  #make positions a column and remove sample name
  platemap$slot <- rownames(platemap)
  mastermixtarget <- platemap
  mastermixtarget$Sample_name <- NULL
  platemap$Gene_name<- NULL
  
  # Convert factor columns to character
  platemap[] <- lapply(platemap, function(col) {
    if (is.factor(col)) as.character(col) else col
  })
  
  # Get unique Gene_names
  unique_samples <- unique(platemap$Sample_name)
  
  # Assign Sample labels to each unique Gene_name
  samplemap <- setNames(paste0("Sample ", seq_along(unique_samples)), unique_samples)
  
  # Map sample labels back to the original plate_map
  platemap$Sample <- sapply(platemap$Sample_name, function(sample) samplemap[[sample]])
  
  #hardcode the amt and mixing + plate deck
  platemap$to_deck <- 2

  #change locsamp columns so it can be combined
  locsamp$samplenames <- rownames(locsamp)
  locsamp$Sample <- sapply(locsamp$samplenames, function(sample) samplemap[[sample]])
  locsamp$samplenames <- NULL
  colnames(locsamp) <- c("from_deck", "from_slot", "Sample")
  
  #combining Locsamp and platemap
  combined <- merge(platemap, locsamp, by= c("Sample"))
  #resorting so human understandable
  combined <- combined[order(as.numeric(sub("Sample ", "", combined$Sample))), ]
  
  #next part until combined is to make sure samples are selected on both mastermix and sample name not just samplename. prefends scenarios where sample 1 goes into mmx 1 and 2 with its tips
  # Get unique Gene_names
  unique_genes <- unique(mastermixtarget$Gene_name)
  
  # Assign Mastermix labels to each unique Gene_name
  mastermix_map <- setNames(paste0("Mastermix ", seq_along(unique_genes)), unique_genes)
  
  # Map Mastermix labels back to the original plate_map
  mastermixtarget$Mastermix <- sapply(mastermixtarget$Gene_name, function(gene) mastermix_map[[gene]])
  res2 <- data.frame(
    to_slot <- mastermixtarget$slot,
    mastermixor <- mastermixtarget$Mastermix
  )
  
  colnames(res2)<- c("slot", "mastermixor")
  combined <- merge(combined, res2, by=c("slot"))
  
  #add a number to sort the sample numbers
  combined$Sample_numeric <- as.numeric(gsub("Sample ", "", combined$Sample))
  
  # Extract alphabetical prefix and numeric suffix from the slot column
  combined$slot_prefix <- gsub("[0-9]+", "", combined$slot)  # Extracts letters
  combined$slot_number <- as.numeric(gsub("[^0-9]", "", combined$slot))  # Extracts numbers
  
  # Sort the data frame by slot_prefix and then slot_number
  combined <- combined[order(combined$slot_prefix, combined$slot_number), ]
  
  # Sort the data frame by the numeric Sample column
  combined_sorted <- combined[order(combined$Sample_numeric), ]
  
  # Remove the helper column if not needed
  combined_sorted$Sample_numeric <- NULL
  combined$slot_prefix <- NULL
  combined$slot_number <- NULL
  
  #format correctly
  res <- data.frame(
    from_deck <- combined_sorted$from_deck,
    from_slot <- combined_sorted$from_slot,
    to_deck <- combined_sorted$to_deck,
    to_slot <- combined_sorted$slot,
    amt <- 4,
    mix <- 1,
    temp <- combined_sorted$mastermixor
  )
  
  colnames(res) <- c("from_deck", "from_slot", "to_deck", "to_slot", "amt", "mix", "originalmm")
  
  tip_n <- tail(cmd_listp$tip_n, n=1)
  asp_set <- tail(cmd_listp$asp_set, n=1)
  
  #set tip_n and asp_set correct for the next part
  tip_n <- tip_n + 1
  asp_set<-asp_set + 1
  
  #just renaming for readability
  cmd_comp <- cmd_listp
  
  #adding n_tip and asp_set
  for(i in 1:nrow(res)){
    cur <- res[i,]
    min <- res[i-1,]
    if(i != 1){
      if (cur$originalmm != min$originalmm | cur$from_slot != min$from_slot){
        tip_n <- tip_n + 1
        asp_set <- asp_set + 1
        res2 <- res[i,]
        pipette <- "NVT"
        comment <- "Plating Sample"
        res2 <- cbind(res2, tip_n, asp_set, pipette, comment)
        res2$originalmm <- NULL
        cmd_comp <- rbind(cmd_comp, res2)
        
      }else{
        res2 <- res[i,]
        pipette <- "NVT"
        comment <- "Plating Sample"
        res2 <- cbind(res2, tip_n, asp_set, pipette, comment)
        res2$originalmm <- NULL
        cmd_comp <- rbind(cmd_comp, res2)
      }
    }else{
      res2 <- res[i,]
      pipette <- "NVT"
      comment <- "Plating Sample"
      res2 <- cbind(res2, tip_n, asp_set, pipette, comment)
      res2$originalmm <- NULL
      cmd_comp <- rbind(cmd_comp, res2)
    }
  }
  rownames(cmd_comp) <- NULL
  
  #sorting because somehow the asp number does weird things
  col_order <- c("from_deck", "from_slot", "to_deck", "to_slot", "amt", "mix", "tip_n", "asp_set", "pipette", "comment")
  cmd_comp <- cmd_comp [,col_order]
  cmd_comp <- cmd_comp[order(cmd_comp$asp_set), ]
  
  return(cmd_comp)
}

#robot handling formatting
rhandcreate<-function(sollist, mastermix, samplelist){
  
  #part 1.1: sollist
  colnames(sollist) <- c("labware", "slot", "RequiredAmount")
  sollist$Name <- rownames(sollist)
  sollist$Catagory <- "STOCK"
  
  sollist$Unit <- "ul"
  rownames(sollist) <- NULL
  rhandler <- data.frame(
    "Catagory" <- sollist$Catagory,
    "Labware" <- sollist$labware,
    "Type" <- "2 Eppy",
    "Slot" <- sollist$slot,
    "Name" <- sollist$Name,
    "RequiredAmount" <- sollist["RequiredAmount"],
    "Unit" <- sollist$Unit
  )
  
  colnames(rhandler)<- c("Catagory", "Labware", "Type", "Slot", "Name", "RequiredAmount", "Unit")
  rhandler <- rhandler %>% mutate(Labware = paste0("labware_", Labware))
  
  #part 1.2 MMix tubes
  mmixtube <- data.frame(
    "Catagory" <- "EMPTY Tubes",
    "Labware"  <- 8,
    "Type" <- "-",
    "Slot" <- "-",
    "Name" <- "2 Eppy",
    "RequiredAmount" <- nrow(mastermix),
    "Unit" <- "tubes"
  )
  colnames(mmixtube) <- colnames(rhandler)
  mmixtube <- mmixtube %>% mutate(Labware = paste0("labware_", Labware))
  
  #part 1.3 samplelist
  sampler <- data.frame(
    "Catagory" <- "Sample",
    "Labware"  <- samplelist$Deck_Id,
    "Type" <- "-",
    "Slot" <- samplelist$Slot_Id,
    "Name" <- rownames(samplelist),
    "RequiredAmount" <- samplelist$ul,
    "Unit" <- "ul"
  )
  colnames(sampler) <- colnames(rhandler)
  sampler <- sampler %>% mutate(Labware = paste0("labware_", Labware))
  
  #list everything
  rhandler <- list(rhandler,
                   mmixtube,
                   sampler
  )
  return(rhandler)
}

#Mainfunctions---------
main <- function(file_path, filename = ""){
  # read excel
  plateMap <- tryCatch({
    GetPlateMap(file_path)
  },
  error = function(cond){
    if(errMessage == ""){
      errMessage <<- "Input file error - plateMap"
    }
    return(NA)
  })
  plate <<- plateMap
  
  
  ReactionNum <- tryCatch({
    GetreactionNum(file_path)
  },
  error = function(cond){
    if(errMessage == ""){
      errMessage <<- "Input file error - Gene names not correct"
    }
    return(NA)
  })
  
  Rnum <<- ReactionNum
  
  #Calc MM components
  Mastermix <- tryCatch({
    MMscheme(ReactionNum)
  },
  error = function(cond){
    if(errMessage == ""){
      errMessage <<- "Mastermix could not be calculated"
    }
    return(NA)
  })
  
  Mastermix <- Mastermix[order(as.numeric(sub(".*?(\\d+)$", "\\1", rownames(Mastermix)))), ]
  mmx <<- Mastermix
  
  #Sollist assignment
  SolList <- tryCatch({
    SolList_fill(Mastermix)
  },
  error = function(cond){
    if(errMessage == ""){
      errMessage <<- "Sollist could not be calculated"
    }
    return(NA)
  })
  sollist <<- SolList
  
  #Sample extract
  samplesdeck <- tryCatch({
    Samplecoll(file_path)
  },
  error = function(cond){
    if(errMessage == ""){
      errMessage <<- "Samples are misbehaving"
    }
    return(NA)
  })
  samples <<- samplesdeck
  
  #mastermix loc
  rows <- LETTERS[1:4]  # Rows A-D
  cols <- 1:6           # Columns 1-6
  slots <- c()
  for (row in rows) {
    slots <- c(slots, paste0(row, cols))
  }
  
  if (errMessage==""){
    last <- tail(SolList, 1)
    
    Mastermix <- fill_positions(
      df = Mastermix,
      start_deck = last$Deck_Id,
      start_slot = last$Slot_Id,
      slots = slots
    )
    
    last_mm <- get_last_position(Mastermix)
    
    SampleList <- fill_positions(
      df = samplesdeck,
      start_deck = last_mm$Deck_Id,
      start_slot = last_mm$Slot_Id,
      slots = slots
    )
    
    #l;ast changes to mmx
    Mastermix$Gene <- NULL
    Mastermix <- Mastermix %>% select(Deck_Id, Slot_Id, everything())
    deckmap <- data.frame(deck=c(1:12), fill = c("Tiprack_P1000", "Plate_A_384", "Tiprack_P50", "Tiprack_P50_2", "Epp_2", "Epp_2_1", "Epp_2_2", "Epp_2_3", "Epp_2_4", "Epp_2_5", "Epp_2_6", "trash"))
    #cmd_list buildup
    cmd_mastermixprep<- cmd_mmprep(SolList, Mastermix)
    
    cmd_plate <- cmd_plate(Mastermix, plateMap, cmd_mastermixprep)
    
    cmd_complete <- cmd_sample(SampleList, plateMap, cmd_plate)
    
    #make the headers
    Sollisthead <- "> SolutionList"
    CMDlisthead <- "> CmdList"
    Decklisthead <- "> DeckMap"
    
    #making the CMDlist output
    rsollist <- SolList
    samplecmd <- SampleList
    samplecmd$Count <- NULL
    samplecmd$ul <- 100
    rsample <- samplecmd
    
    SolList <- rbind.data.frame(SolList, samplecmd)
    
    #Making Sollist and deckmap the same column
    dis <- replicate(length(SolList[,1]), "NA")
    x <- rownames(SolList)
    cmd_sollist <- cbind.data.frame(SolList[,c(1,2)], SolList[,3], x, dis, dis, dis, dis, dis, dis, stringsAsFactors=F)
    cmd_sollisttest2 <<- cmd_sollist
    colnames(cmd_sollist) <- colnames(cmd_complete)
    
    dis <- replicate(length(deckmap[,1]), "NA")
    deckmap <- cbind.data.frame(deckmap, dis, dis, dis, dis, dis, dis, dis, dis)
    
    cmdList_output <<- list(Sollisthead, cmd_sollist,
                            CMDlisthead, cmd_complete,
                            Decklisthead, deckmap
    )
    #Robothandler/user commands ------
    Rhandlerp1 <- rhandcreate(rsollist, Mastermix, rsample)
    usercmd_output <<- Rhandlerp1
    
  }else{
    SolList <- errMessage
  }
  
  displaysollist <- cmd_sollist[c(1,2,3)]
  displaysollist$what <- rownames(displaysollist)
  
  displaylist <- displaysollist
    
  colnames(displaylist) <- c("Deck location", "Slot", "Required Amount", "What")
  return(displaylist)
}



# #TEST--------------
# # input
# errMessage <<- ""
# fileName <- "qPCRTemplate384_PlateMap_128.xlsx"
# #fileName <- "qPCRTemplate384_PlateMap.xlsx"
# mainwd <- "C:\\Users\\jornb\\Documents\\GitHub\\ot2\\upstream (R) processors\\384qPCR"
# input_file_name <- paste0(mainwd, "\\", fileName)
# #
# output <- main(input_file_name)