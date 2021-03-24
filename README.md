# GIFTs: Ensembl Production Service

There are two GIFTs pipelines which can be run and monitored with this service.

One pipeline loads Ensembl genes into the GIFTs database, and the other
performs alignments between Ensembl and UniProt data. Jobs are seeded in
these pipelines by submitting requests to the 'Update Ensembl' or
'Process Mappings' endpoints, respectively.
