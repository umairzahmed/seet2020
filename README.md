# Characterizing the Pedagogical Benefits of Adaptive Feedback for Compilation Errors by Novice Programmers
Artifacts of an ICSE SEET 2020 paper titled: Characterizing the Pedagogical Benefits of Adaptive Feedback for Compilation Errors by Novice Programmers.

In a large-scale experiment, we compare student performance when tutored
by human tutors, and when receiving automated adaptive feedback.
The automated feedback was designed using one of two ell-known
instructional principles: (i) presenting the correct solution for the
immediate problem, or (ii) presenting generated examples or analogies
that guide towards the correct solution. We report empirical
results from a large-scale (N = 480, 10,000+ person hour) experiment
assessing the efficacy of these automated compilation-error feedback
tools. 

Using the survival analysis on error rates of students measured over seven weeks, we found that automated feedback allows students to resolve errors in their code more efficiently than students receiving manual feedback. However, we also found that this advantage is primarily logistical and not conceptual; the performance benefit seen during lab assignments disappeared during exams wherein feedback of any kind was withdrawn. We further found that the performance advantage of automated feedback over human tutors increases with problem complexity, and that feedback via example and specific repair have distinct, non-overlapping relative advantages for different categories of programming errors. Our results offer a clear and granular delimitation of the pedagogical
benefits of automated feedback in teaching programming to novices.

## Contributors
- [Umair Z. Ahmed](https://www.cse.iitk.ac.in/users/umair/)<sup>*</sup>, [National University of Singapore](https://www.comp.nus.edu.sg/)
- [Nisheeth Srivastava](https://www.cse.iitk.ac.in/users/nsrivast/), [IIT Kanpur](https://www.cse.iitk.ac.in/)
- [Renuka Sindhgatta](https://staff.qut.edu.au/staff/renuka.sindhgattarajan), [Queensland University of Technology](https://www.qut.edu.au/)
- [Amey Karkare](https://www.cse.iitk.ac.in/users/karkare/), [IIT Kanpur](https://www.cse.iitk.ac.in/)

<sup>*</sup> Part of this work was carried out by the author at [IIT Kanpur](https://www.cse.iitk.ac.in/).

## Publication
If you use any part of our dataset or analysis/plot scripts, then please do cite our [ICSE-SEET-2020 paper](doc/ICSE-SEET-2020_paper-24.pdf).

```
@inproceedings{ahmed2020AdaptiveFeedback,
    title={Characterizing the Pedagogical Benefits of Adaptive Feedback for Compilation Errors by Novice Programmers},
    author={Ahmed, Umair Z. and Srivastava, Nisheeth and Sindhgatta, Renuka and Karkare, Amey},
    booktitle={Proceedings of the 42nd International Conference on Software Engineering: Software Engineering Education and Training},
    year={2020}
}
```

If you use any part of our dataset, then please cite both [ICSE-SEET-2020](doc/ICSE-SEET-2020_paper-24.pdf) which released this dataset, as well as [Prutor IDE paper](https://arxiv.org/pdf/1608.03828.pdf) which collated this dataset.

```
@article{das2016prutor,
  title={Prutor: A system for tutoring CS1 and collecting student programs for analysis},
  author={Das, Rajdeep and Ahmed, Umair Z. and Karkare, Amey and Gulwani, Sumit},
  journal={arXiv preprint arXiv:1608.03828},
  year={2016}
}
```

## Dataset
Our student code repository consists of code attempts made by students, during the 2016-2017-II, 2017-2018-I and 2017-2018-II semester course offering of Introductory to C Programming (CS1) at [IIT Kanpur](http://www.iitk.ac.in/), a large public university. This course was credited by 400+ first year undergraduate students, who attempted 40+ different programming assignments as part of course requirement. These assignments were completed on a custom web-browser based IDE [Prutor](https://www.cse.iitk.ac.in/users/karkare/prutor/), which records all intermediate code attempts.


## Setup
### Ubuntu/Debian packages
`sudo apt install pip3 unzip`

### Extract dataset
`unzip -d ./data/ ./data/data.zip`

### Python packages
`pip3 install --version requirements.txt`

## Scripts
All plots reported in paper can be obtained using the Jupyter notebook file [plots.ipynb](./plots.ipynb)

`jupyter notebook`