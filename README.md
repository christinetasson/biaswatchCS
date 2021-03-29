# BiasWatchCS

The purpose of this repository is to watch biases in Computer Science conferences from files extracted from EasyChair.org.

It is largely inspired from https://biaswatchneuro.com

# How to extract files from http://easychair.org

- Access to your conference as a `chair`
- Choose `Premium > Conference Data Download > CSV data`
  - Check boxes Program committee (`committee.csv`), Submissions (`submission.csv`), Authors(`author.csv`), Reviews(`review.csv`)\\
  - Keep only `firstname` and `code` of country columns
- Choose `Administration > Other utilities > List of accepted submissions`
  - From files `submission.csv`, `author.csv` and the List of accepted submissions, extract a csv file with two columns with headers *firstname* and *country* of authors with at least one accepted submission.

# How statistics are computed ?

- The input is a `.csv` file with headers: 'firstname' and 'country'. 
- Each  *firstname* is associated to a *gender* with probability from the API https://genderize.io using the python library https://pypi.org/project/Genderize/.

- Each *code* of a country (like FR for France) is associated to a *geographical area* as classified by United Nations https://unstats.un.org/unsd/methodology/m49/.

- The output is a statistics printed on the standard output and in a file `stat.csv`.
