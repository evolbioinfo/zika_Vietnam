suppressPackageStartupMessages(require(ape))
suppressPackageStartupMessages(require(treedater))
suppressPackageStartupMessages(require(foreach))
suppressPackageStartupMessages(require(getopt))

spec = matrix(c(
  'help', 'h', 0, "logical",
  'tree', 't', 1, "character",
  'out_tree', 'o', 1, "character",
  'dates', 'd', 1, "character",
  'out_log', 'l', 1, "character",
  'seqlen', 's', 1, "numeric",
  'threads', 'm', 2, "numeric",
  'pdf', 'p', 1, "character",
  'outliers', 'u', 1, "character",
  'root', 'r', 1, "numeric"
), byrow=TRUE, ncol=4)
opt = getopt(spec)

if (!is.null(opt$help)) {
  cat(getopt(spec, usage=TRUE))
  q(status=1)
}

if (is.null(opt$threads)) {
    opt$threads=1
}

in.nwk = opt$tree
in.dates = opt$dates
out.nwk = opt$out_tree
out.log = opt$out_log
seq.len = opt$seqlen
threads = opt$threads
out.pdf = opt$pdf
out.outliers = opt$outliers
root=opt$root!=0

tre = read.tree(in.nwk)
if (root) {
    tre = unroot(tre)
}
dates = read.table(in.dates, sep=',', header=FALSE)
names(dates) = c('accession', 'date', 'lower', 'upper')
row.names(dates) = dates$accession
dates = dates[-c(1)]
tre = drop.tip(tre, setdiff(tre$tip.label, row.names(dates)))

dates = dates[tre$tip.label,]
ds = dates$date
names(ds) = row.names(dates)
ds = ds[!is.na(ds)]
dates = dates[is.na(dates$date),]
dates = dates[-c(1)]
if (nrow(dates) == 0) {
    dates = NULL
}

res = dater(tre, sts=ds, s=seq.len, estimateSampleTimes=dates, searchRoot=10, ncpu=threads, minblen=1/12.)
summary(res)

outlier.df = outlierTips(res)
write.csv(outlier.df, out.outliers, row.names=FALSE)
outliers = as.vector(outlier.df[outlier.df$q < .05,]$taxon)
if (length(outliers) > 0) {
    print(paste("Removed ", length(outliers), " outliers: ", paste(outliers, collapse=', ')))
    tre = drop.tip(tre, outliers)
    res = dater(tre, sts=ds, s=seq.len, estimateSampleTimes=dates, searchRoot=10, ncpu=threads, minblen=1/12.)
    summary(res)
}

write.tree(res, file=out.nwk)

pdf(out.pdf)
fit = rootToTipRegressionPlot(res)
summary(fit)
plot(fit)
dev.off()


v = res[c("clock", "meanRate", "timeOfMRCA", "loglik", "r")]
write.csv(v, out.log, row.names=FALSE)

pb = parboot(res, nreps=100, ncpu=threads, overrideTempConstraint=TRUE, overrideClock=NULL, overrideSearchRoot=TRUE)
v = c(res[c("clock", "meanRate", "timeOfMRCA", "loglik", "r")], pb[c("meanRate_CI", "timeOfMRCA_CI", "coef_of_variation_CI")])
write.csv(v, out.log, row.names=FALSE)
summary(pb)
