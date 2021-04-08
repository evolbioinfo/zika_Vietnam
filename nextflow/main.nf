ref=file("data/sequence.fasta")
bams = Channel.fromPath("data/*.bam")
multiconfig=file("data/multiqc_config.yaml")
k2db=file("data/minikraken2_v2_8GB_201904_UPDATE/")
results="results"

process toFastQ{
    label 'samtools'

    input:
    file bam from bams

    output:
    file "${bam.baseName}.fq" into fastqs, fastqs2, fastqs3, fastqs4, fastqs5

    script:
    """
    samtools fastq -0 ${bam.baseName}.fq  ${bam}
    """
}

process nanoplot {
   publishDir "$results/qc/nanoplot/${fastq.baseName}/", mode: 'copy'

   label 'nanoplot'
   
   input:
   file fastq from fastqs3

   output:
   file "*.{png,html,txt,log}" into nanoplot

   script:
   """
   NanoPlot -t ${task.cpus} --fastq ${fastq}
   """
}

process fastqc {
   publishDir "$results/qc/fastqc/${fastq.baseName}/", mode: 'copy'

   label 'fastqc'
   
   input:
   file fastq from fastqs4

   output:
   file "*.{zip,html}" into fastqc

   script:
   """
   fastqc -q -t $task.cpus ${fastq}
   """
}


process map{
    label 'minimap'

    input:
    file fastq from fastqs
    file ref

    output:
    file "${fastq.baseName}.sam" into sams

    script:
    """
    minimap2 -a ${ref} ${fastq} -o ${fastq.baseName}.sam
    """
}

process toBam{
    publishDir "$results/bam", mode: 'copy'

    label 'samtools'

    input:
    file sam from sams

    output:
    set file("${sam.baseName}.bam"), file("${sam.baseName}.bam.bai") into bam
    file "${sam.baseName}.txt" into flagstats

    script:
    """
    samtools view -bh ${sam} | samtools sort > ${sam.baseName}.bam
    samtools index ${sam.baseName}.bam
    samtools flagstat ${sam.baseName}.bam > ${sam.baseName}.txt
    """
}

process assign{

   label 'kraken'

   input:
   file fastq from fastqs5
   file k2db

   output:
   file "${fastq.baseName}.txt" into krakenreports   

   script:
   """
   kraken2 --db minikraken2_v2_8GB_201904_UPDATE --threads ${task.cpus} --report ${fastq.baseName}.txt  ${fastq} > ${fastq.baseName}.kraken2 
   """
}

process multiqc {
   publishDir "$results/qc/multiqc", mode: 'copy'

   label 'multiqc'
   
   input:
   file ('fastqc/*') from fastqc.collect().ifEmpty([])
   file ('flagstat/*') from flagstats.collect().ifEmpty([])
   file ('kraken/*') from krakenreports.collect().ifEmpty([])
   file config from multiconfig

   
   output:
   file "*multiqc_report.html" into ch_multiqc_report
   file "*_data"

   script:
   """
   multiqc .  -c ${config} -m fastqc -m samtools -m kraken
   """
}


process assemble {
    publishDir "$results/assembly", mode: 'copy'

    label 'canu'

    input:
    file fastq from fastqs2

    output:
    file "zika/*.contigs.fasta" into contigs

    script:
    """
    canu -p ${fastq.baseName} -d zika genomeSize=10.8k minReadLength=200 minOverlapLength=50 maxMemory=${task.memory.toMega()}m maxThreads=${task.cpus} -nanopore ${fastq}
    """
}

process remap {
	
   label 'minimap'

   input:
   file contig from contigs
   file ref

   output:
   file "*.sam" into remaps

   script:
   """
   minimap2 -ax splice ${ref} ${contig} > ${contig.baseName}_remap.sam
   """
}

process remapToBam {
   publishDir "$results/bam", mode: 'copy'

   label 'samtools'

   input:
   file sam from remaps

   output:
   file "${sam.baseName}.bam"
   file "${sam.baseName}.bam.bai"

   script:
   """
   samtools view -bh ${sam} | samtools sort > ${sam.baseName}.bam
   samtools index ${sam.baseName}.bam
   """
}

process consensus {
   publishDir "$results/consensus/", mode: 'copy'

   label 'bcftools'

   input:
   set file(bamfile), file(baifile) from bam
   file ref

   output:
   file "${bamfile.baseName}.fasta" into consensus

   script:
   """
   # Call variants
   bcftools mpileup -d 1000000 -Ou -f ${ref} ${bamfile} | bcftools call --ploidy 1 -m -Oz -o calls.vcf.gz
   bcftools index calls.vcf.gz

   # Normalize indels
   bcftools norm -f ${ref} calls.vcf.gz -Ob -o calls.norm.bcf
   bcftools index calls.norm.bcf

   # Filter adjacent indels within 5bp
   bcftools filter --IndelGap 5 calls.norm.bcf -Oz > calls.norm.flt-indels.vcf.gz
   bcftools index calls.norm.flt-indels.vcf.gz

   # Consensus
   bcftools consensus -M N -a N -i "QUAL>20 && DP>50" -f ${ref} calls.norm.flt-indels.vcf.gz > tmp
   sed 's/>.*/>${bamfile.baseName}/' tmp > ${bamfile.baseName}.fasta
   rm tmp
   """
}
