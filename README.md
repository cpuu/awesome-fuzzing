# Fuzzing [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of awesome Fuzzing for software security


## Table of Contents

- [Books](#books)
- [Papers](#papers)
- [Tools](#tools)
- [Platform](#platform)


## Books
- [Fuzzing for Software Security Testing and Quality Assurance, 2nd Edition](https://www.amazon.com/Fuzzing-Software-Security-Testing-Assurance/dp/1608078507/) (2018)
- [Fuzzing: Brute Force Vulnerability Discovery, 1st Edition](https://www.amazon.com/Fuzzing-Brute-Force-Vulnerability-Discovery/dp/0321446119/) (2007)
- [Open Source Fuzzing Tools, 1st Edition](https://www.amazon.com/Open-Source-Fuzzing-Tools-Rathaus/dp/1597491950/) (2007)


## Papers
### The Network and Distributed System Security Symposium (NDSS)
- [Vuzzer: Application-aware evolutionary fuzzing, 2017](https://www.researchgate.net/profile/Cristiano_Giuffrida/publication/311886374_VUzzer_Application-aware_Evolutionary_Fuzzing/links/585f3f5608aebf17d38d5678/VUzzer-Application-aware-Evolutionary-Fuzzing.pdf)
- [Driller: Augmenting Fuzzing Through Selective Symbolic Execution, 2016](https://cancer.shtech.org/wiki/uploads/2016---NDSS---driller-augmenting-fuzzing-through-selective-symbolic-execution.pdf)
### ACM Conference on Computer and Communications Security (ACM CCS)
- [IMF: Inferred Model-based Fuzzer, 2017](http://daramg.gift/paper/han-ccs2017.pdf)
- [SemFuzz: Semantics-based Automatic Generation of Proof-of-Concept Exploits, 2017](https://www.informatics.indiana.edu/xw7/papers/p2139-you.pdf)
- [AFL-based Fuzzing for Java with Kelinci, 2017](https://www.andrew.cmu.edu/user/rkersten/publications/ccs17-kersten.pdf)
- [Designing New Operating Primitives to Improve Fuzzing Performance, 2017](http://iisp.gatech.edu/sites/default/files/images/designing_new_operating_primitives_to_improve_fuzzing_performance_vt.pdf)
- [Directed Greybox Fuzzing, 2017](https://www.comp.nus.edu.sg/~mboehme/paper/CCS17.pdf)
- [SlowFuzz: Automated Domain-Independent Detection of Algorithmic Complexity Vulnerabilities, 2017](https://arxiv.org/pdf/1708.08437.pdf)
- [DIFUZE: Interface Aware Fuzzing for Kernel Drivers, 2017](https://acmccs.github.io/papers/p2123-corinaA.pdf), [github](https://github.com/ucsb-seclab/difuze)
- [Systematic Fuzzing and Testing of TLS Libraries, 2016](https://www.nds.rub.de/media/nds/veroeffentlichungen/2016/10/19/tls-attacker-ccs16.pdf)
- [Coverage-based Greybox Fuzzing as Markov Chain, 2016](https://ieeexplore.ieee.org/abstract/document/8233151)
- [eFuzz: A Fuzzer for DLMS/COSEM Electricity Meters, 2016](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.817.5616&rep=rep1&type=pdf)
- [Scheduling Black-box Mutational Fuzzing, 2013](https://softsec.kaist.ac.kr/~sangkilc/papers/woo-ccs13.pdf)
- [Taming compiler fuzzers, 2013](https://www.cs.utah.edu/~regehr/papers/pldi13.pdf)
- [SAGE: whitebox fuzzing for security testing, 2012](https://dl.acm.org/citation.cfm?id=2094081)
- [Grammar-based whitebox fuzzing, 2008](https://dl.acm.org/citation.cfm?id=1375607)
### USENIX Security
- [MoonShine: Optimizing OS Fuzzer Seed Selection with Trace Distillation, 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/pailoor)
- [QSYM : A Practical Concolic Execution Engine Tailored for Hybrid Fuzzing, 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/yun)
- [OSS-Fuzz - Google's continuous fuzzing service for open source software, 2017](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/serebryany)
- [kAFL: Hardware-Assisted Feedback Fuzzing for OS Kernels, 2017](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/schumilo)
- [Protocol State Fuzzing of TLS Implementations, 2015](https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/de-ruiter)
- [Optimizing Seed Selection for Fuzzing, 2014](https://softsec.kaist.ac.kr/~sangkilc/papers/rebert-usenixsec14.pdf)
- [Dowsing for overflows: a guided fuzzer to find buffer boundary violations, 2013](http://enigma.usenix.org/sites/default/files/sec13_proceedings_interior.pdf#page=57)
- [Fuzzing with Code Fragments, 2012](https://www.usenix.org/system/files/conference/usenixsecurity12/sec12-final73.pdf)
### IEEE Symposium on Security and Privacy (IEEE S&P)
- [Angora: Efficient Fuzzing by Principled Search, 2018](http://web.cs.ucdavis.edu/~hchen/paper/chen2018angora.pdf)
- [CollAFL: Path Sensitive Fuzzing, 2018](http://chao.100871.net/papers/oakland18.pdf)
- [T-Fuzz: fuzzing by program transformation, 2018](https://nebelwelt.net/publications/files/18Oakland.pdf)
- [Skyfire: Data-Driven Seed Generation for Fuzzing, 2017](https://www.ieee-security.org/TC/SP2017/papers/42.pdf)
- [Program-Adaptive Mutational Fuzzing, 2015](https://softsec.kaist.ac.kr/~sangkilc/papers/cha-oakland15.pdf)
- [TaintScope: A checksum-aware directed fuzzing tool for automatic software vulnerability detection, 2010](https://ieeexplore.ieee.org/abstract/document/5504701)
- [Taint-based directed whitebox fuzzing, 2009](https://dl.acm.org/citation.cfm?id=1555061)
### ArXiv (Fuzzing with Artificial Intelligence & Machine Learning)
- [Coverage-Guided Fuzzing for Deep Neural Networks, 2018](https://arxiv.org/abs/1809.01266)
- [DLFuzz: Differential Fuzzing Testing of Deep Learning Systems, 2018](https://arxiv.org/abs/1808.09413)
- [TensorFuzz: Debugging Neural Networks with Coverage-Guided Fuzzing, 2018](https://arxiv.org/abs/1807.10875)
- [NEUZZ: Efficient Fuzzing with Neural Program Learning, 2018](https://arxiv.org/abs/1807.05620)
- [EnFuzz: From Ensemble Learning to Ensemble Fuzzing, 2018](https://arxiv.org/abs/1807.00182)
- [REST-ler: Automatic Intelligent REST API Fuzzing, 2018](https://arxiv.org/abs/1806.09739)
- [Deep Reinforcement Fuzzing, 2018](https://arxiv.org/abs/1801.04589)
- [Not all bytes are equal: Neural byte sieve for fuzzing, 2017](https://arxiv.org/abs/1711.04596)
- [Faster Fuzzing: Reinitialization with Deep Neural Models, 2017](https://arxiv.org/abs/1711.02807)
- [Learn&Fuzz: Machine Learning for Input Fuzzing, 2017](https://arxiv.org/abs/1701.07232)
- [Complementing Model Learning with Mutation-Based Fuzzing, 2016](https://arxiv.org/abs/1611.02429)
### The others
- [Ifuzzer: An evolutionary interpreter fuzzer using genetic programming, 2016](https://www.cs.vu.nl/~herbertb/download/papers/ifuzzer-esorics16.pdf)
- [Hybrid fuzz testing: Discovering software bugs via fuzzing and symbolic execution, 2012](https://pdfs.semanticscholar.org/488a/b1e313f5109153f2c74e3b5d86d41e9b4b71.pdf)
- [Call-Flow Aware API Fuzz Testing for Security of Windows Systems, 2008](https://www.computer.org/csdl/proceedings/iccsa/2008/3243/00/3243a019-abs.html)
- [Randoop : Feedback-directed random test generation, 2007](https://dl.acm.org/citation.cfm?id=1248841)



## Tools
About this section. Optional. Keep this short and focus on the list.
### General-purpose
- [radamsa](https://gitlab.com/akihe/radamsa) is a general-purpose fuzzer.
### Binary
- [American fuzzy lop](http://lcamtuf.coredump.cx/afl/) is a security-oriented fuzzer that employs a novel type of compile-time instrumentation and genetic algorithms to automatically discover clean, interesting test cases that trigger new internal states in the targeted binary. 
- [WinAFL](https://github.com/googleprojectzero/winafl) is a fork of AFL for fuzzing Windows binaries.
- [libFuzzer](http://llvm.org/docs/LibFuzzer.html) is a library for coverage-guided fuzz testing. [Tutorial from Google](https://github.com/google/fuzzer-test-suite/blob/master/tutorial/libFuzzerTutorial.md)
- [Driller](https://github.com/shellphish/driller) is an implementation of the [driller paper](https://www.cs.ucsb.edu/~vigna/publications/2016_NDSS_Driller.pdf). This implementation was built on top of AFL with angr being used as a symbolic tracer.
- [shellphish fuzzer](https://github.com/shellphish/fuzzer) is a python interface to AFL, allowing for easy injection of testcases and other functionality.
### Web, JavaScript
- [jsfunfuzz](https://github.com/MozillaSecurity/funfuzz) - JavaScript engine fuzzers
- [IFuzzer](https://github.com/vspandan/IFuzzer)
- [domato](https://github.com/googleprojectzero/domato) - DOM fuzzer from [Google Project Zero](https://github.com/googleprojectzero). [Blog Post](https://googleprojectzero.blogspot.com/2017/09/the-great-dom-fuzz-off-of-2017.html)
### Network protocol
- [boofuzz](https://github.com/jtpereyda/boofuzz) : Network Protocol Fuzzing for Humans. Documentation is available at http://boofuzz.readthedocs.io/, including nifty quickstart guides.
- [TumbleRF](https://github.com/riverloopsec/tumblerf) is a framework that orchestrates the application of fuzzing techniques to RF systems. 
### Platform
- [Blackhat USA 2018 AFL workshop training materials](https://github.com/wrauner/afl-fuzzing-training) by [@wrauner](https://github.com/wrauner)

## Contribute

Contributions welcome! Read the [contribution guidelines](contributing.md) first.


## License

[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](http://creativecommons.org/publicdomain/zero/1.0)

To the extent possible under law, cpuu has waived all copyright and
related or neighboring rights to this work.
