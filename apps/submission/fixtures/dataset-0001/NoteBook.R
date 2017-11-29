############################################################
# Title : First dataset to be imported in Pixel
# Organism : Candida glabrata
# Omics area : Proteomic
# Pixeler : Thomas DENECKER and Gaelle LELANDAIS
# Date : October, Wednesday 25th, 2017
###########################################################

###########################################################
# R and packages version
###########################################################

# R version :: 3.4.2
# Limma package version :: 3.32.10

###########################################################
# Library
###########################################################

library(limma)

###############################################
# Main                                        #
###############################################

# To change column name
colonne_names = c("C10_1", "C10_2", "RB1_10_1","RB1_10_2", "RB2_10_1","RB2_10_2", 
                  "C60_1", "C60_2", "RB1_60_1", "RB1_60_2", "RB2_60_1", "RB2_60_2" )

# Data reading
ProG_glabratai = read.csv2("./1503002-protein-measurements-PD2.1.csv", header = T,
                          sep = ",", row.names = 1, skip = 2,  stringsAsFactors = FALSE)
# Extract column with Normalized Abundance values
ProG_glabrata = ProG_glabratai[, 9:20]
colnames(ProG_glabrata) = colonne_names

# convert data to ensure numeric values
for(i in 1:12){
  ProG_glabrata[,i] = as.numeric(as.character(ProG_glabrata[,i]))
}

# Abundance values that equal 0 are replaced by NA
ProG_glabrata[which(ProG_glabrata == 0, arr.ind=T)] = NA

# Verification that each protein has (at least) one abundance value
comp = 0
for (i in 1:dim(ProG_glabrata)[1]){
  if(length(na.omit(ProG_glabrata[i,]))!=0)
    comp = comp +1
}

########################################################################################################################
# Calculation of logFC             
########################################################################################################################

# mean values for C10 and C60 conditions
c10= apply(ProG_glabrata[,1:2], 1 , mean)
c60= apply(ProG_glabrata[,7:8], 1 , mean)

# logFC values
logFC_table = cbind("log(RB1_1_10/c10)" = log(ProG_glabrata$RB1_10_1/c10),
                    "log(RB1_2_10/c10)" = log(ProG_glabrata$RB1_10_2/c10), 
                    "log(RB2_1_10/c10)"= log(ProG_glabrata$RB2_10_1/c10), 
                    "log(RB2_2_10/c10)"= log(ProG_glabrata$RB2_10_2/c10), 
                    "log(RB1_1_60/c60)" =log(ProG_glabrata$RB1_60_1/c60), 
                    "log(RB1_2_60/c60)" =log(ProG_glabrata$RB1_60_2/c60),
                    "log(RB2_1_60/c60)"= log(ProG_glabrata$RB2_60_1/c60), 
                    "log(RB2_2_60/c60)"= log(ProG_glabrata$RB2_60_2/c60))


#########################################################
# LIMMA - glabrata
#########################################################

# C10
fit = lmFit(cbind(logFC_table[,1:4]))
limmaRes = eBayes(fit)
limmaTableC10 = topTable(limmaRes, number = nrow(logFC_table))

# C60
fit = lmFit(cbind(logFC_table[,5:8]))
limmaRes = eBayes(fit)
limmaTableC60 = topTable(limmaRes, number = nrow(logFC_table))

# Preparation to export 
table_export_limmaTableC10 = cbind(OmicsUnit = rownames(limmaTableC10), 
                                   limmaTableC10[,c("logFC", "P.Value")])
colnames(table_export_limmaTableC10 ) = c("OmicsUnit", "Value", "Quality_score")

table_export_limmaTableC60 = cbind(rownames(limmaTableC60), 
                                   limmaTableC60[,c("logFC", "P.Value")])
colnames(table_export_limmaTableC60 ) = c("OmicsUnit", "Value", "Quality_score")

# export pixels
write.table(table_export_limmaTableC10, file = "Pixel_C10.txt", row.names = F, quote = F)
write.table(table_export_limmaTableC60, file = "Pixel_C60.txt", row.names = F, quote = F)
