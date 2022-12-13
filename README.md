# Awesome Fuzzing [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> [Fuzzing](https://en.wikipedia.org/wiki/Fuzzing) or fuzz testing is an automated software testing technique that involves providing invalid, unexpected, or random data as inputs to a computer program. The program is then monitored for exceptions such as crashes, failing built-in code assertions, or potential memory leaks. Typically, fuzzers are used to test programs that take structured inputs. 

A curated list of references to awesome Fuzzing for security testing. Additionally there is a collection of freely available academic papers, tools and so on.

Your favorite tool or your own paper is not listed? Fork and create a Pull Request to add it!


## Contents

- [Books](#books)
- [Papers](#papers)
- [Tools](#tools)
- [Platform](#platform)


## Books
- [Fuzzing-101](https://github.com/antonio-morales/Fuzzing101)
- [The Fuzzing Book](https://www.fuzzingbook.org/) (2019)
- [The Art, Science, and Engineering of Fuzzing: A Survey](https://ieeexplore.ieee.org/document/8863940) (2019) - 
Actually, this document is a paper, but it contains more important and essential content than any other book.
- [Fuzzing for Software Security Testing and Quality Assurance, 2nd Edition](https://www.amazon.com/Fuzzing-Software-Security-Testing-Assurance/dp/1608078507/) (2018)
- [Fuzzing: Brute Force Vulnerability Discovery, 1st Edition](https://www.amazon.com/Fuzzing-Brute-Force-Vulnerability-Discovery/dp/0321446119/) (2007)
- [Open Source Fuzzing Tools, 1st Edition](https://www.amazon.com/Open-Source-Fuzzing-Tools-Rathaus/dp/1597491950/) (2007)


## Talks
- [Fuzzing Labs - Patrick Ventuzelo](https://www.youtube.com/channel/UCGD1Qt2jgnFRjrfAITGdNfQ), Youtube
- [Effective File Format Fuzzing](https://youtu.be/qTTwqFRD1H8), Black Hat Europe 2016
- [Adventures in Fuzzing](https://www.youtube.com/watch?v=SngK4W4tVc0), NYU Talk 2018
- [Fuzzing with AFL](https://www.youtube.com/watch?v=DFQT1YxvpDo), NDC Conferences 2018

## Papers
To achieve a well-defined scope, I have chosen to include publications on fuzzing in the last proceedings of 4
top major security conferences and others from Jan 2008 to Jul 2019.
It includes (i) Network and Distributed System Security Symposium (NDSS), (ii) IEEE Symposium on
Security and Privacy (S&P), (iii) USENIX Security Symposium (USEC), and (iv) ACM Conference on Computer and Communications Security (CCS).


### The Network and Distributed System Security Symposium (NDSS)
- [Semantic-Informed Driver Fuzzing Without Both the Hardware Devices and the Emulators, 2022](https://www.ndss-symposium.org/wp-content/uploads/2022-345-paper.pdf)
- [MobFuzz: Adaptive Multi-objective Optimization in Gray-box Fuzzing, 2022](https://www.ndss-symposium.org/wp-content/uploads/2022-314-paper.pdf)
- [Context-Sensitive and Directional Concurrency Fuzzing for Data-Race Detection, 2022](https://www.ndss-symposium.org/wp-content/uploads/2022-296-paper.pdf)
- [EMS: History-Driven Mutation for Coverage-based Fuzzing, 2022](https://www.ndss-symposium.org/wp-content/uploads/2022-162-paper.pdf)
- [WINNIE : Fuzzing Windows Applications with Harness Synthesis and Fast Cloning, 2021](https://taesoo.kim/pubs/2021/jung:winnie.pdf)
- [Reinforcement Learning-based Hierarchical Seed Scheduling for Greybox Fuzzing, 2021](https://www.cs.ucr.edu/~heng/pubs/afl-hier.pdf)
- [PGFUZZ: Policy-Guided Fuzzing for Robotic Vehicles, 2021](https://beerkay.github.io/papers/Berkay2021PGFuzzNDSS.pdf)
- [Favocado: Fuzzing Binding Code of JavaScript Engines Using Semantically Correct Test Cases, 2021](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_6A-2_24224_paper.pdf)
- [HFL: Hybrid Fuzzing on the Linux Kernel, 2020](https://www.unexploitable.systems/publication/kimhfl/)
- [HotFuzz: Discovering Algorithmic Denial-of-Service Vulnerabilities Through Guided Micro-Fuzzing, 2020](https://www.researchgate.net/publication/339164746_HotFuzz_Discovering_Algorithmic_Denial-of-Service_Vulnerabilities_Through_Guided_Micro-Fuzzing)
- [HYPER-CUBE: High-Dimensional Hypervisor Fuzzing, 2020](https://www.syssec.ruhr-uni-bochum.de/media/emma/veroeffentlichungen/2020/02/07/Hyper-Cube-NDSS20.pdf)
- [Not All Coverage Measurements Are Equal: Fuzzing by Coverage Accounting for Input Prioritization, 2020](https://www.ndss-symposium.org/wp-content/uploads/2020/02/24422.pdf)
- [CodeAlchemist: Semantics-Aware Code Generation to Find Vulnerabilities in JavaScript Engines, 2019](https://daramg.gift/paper/han-ndss2019.pdf)
- [PeriScope: An Effective Probing and Fuzzing Framework for the Hardware-OS Boundary, 2019](https://people.cs.kuleuven.be/~stijn.volckaert/papers/2019_NDSS_PeriScope.pdf)
- [REDQUEEN: Fuzzing with Input-to-State Correspondence, 2019](https://www.syssec.ruhr-uni-bochum.de/media/emma/veroeffentlichungen/2018/12/17/NDSS19-Redqueen.pdf)
- [Send Hardest Problems My Way: Probabilistic Path Prioritization for Hybrid Fuzzing, 2019](https://www.cs.ucr.edu/~heng/pubs/digfuzz_ndss19.pdf)
- [Life after Speech Recognition: Fuzzing Semantic Misinterpretation for Voice Assistant Applications, 2019](https://www.ndss-symposium.org/wp-content/uploads/2019/02/ndss2019_08-4_Zhang_paper.pdf)
- [INSTRIM: Lightweight Instrumentation for Coverage-guided Fuzzing, 2018](https://www.ndss-symposium.org/wp-content/uploads/2018/07/bar2018_14_Hsu_paper.pdf)
- [IoTFuzzer: Discovering Memory Corruptions in IoT Through App-based Fuzzing, 2018](http://wp.internetsociety.org/ndss/wp-content/uploads/sites/25/2018/02/ndss2018_01A-1_Chen_paper.pdf)
- [What You Corrupt Is Not What You Crash: Challenges in Fuzzing Embedded Devices, 2018](http://s3.eurecom.fr/docs/ndss18_muench.pdf)
- [Enhancing Memory Error Detection for Large-Scale Applications and Fuzz Testing, 2018](https://lifeasageek.github.io/papers/han:meds.pdf)
- [Vuzzer: Application-aware evolutionary fuzzing, 2017](https://www.ndss-symposium.org/ndss2017/ndss-2017-programme/vuzzer-application-aware-evolutionary-fuzzing/)
- [DELTA: A Security Assessment Framework for Software-Defined Networks, 2017](https://www.ndss-symposium.org/wp-content/uploads/2017/09/ndss201702A-1LeePaper.pdf)
- [Driller: Augmenting Fuzzing Through Selective Symbolic Execution, 2016](https://cancer.shtech.org/wiki/uploads/2016---NDSS---driller-augmenting-fuzzing-through-selective-symbolic-execution.pdf)
- [Automated Whitebox Fuzz Testing, 2008](https://www.ndss-symposium.org/wp-content/uploads/2017/09/Automated-Whitebox-Fuzz-Testing-paper-Patrice-Godefroid.pdf)


### IEEE Symposium on Security and Privacy (IEEE S&P)
- [PATA: Fuzzing with Path Aware Taint Analysis, 2022](http://www.wingtecher.com/themes/WingTecherResearch/assets/papers/sp22.pdf)
- [Jigsaw: Efficient and Scalable Path Constraints Fuzzing, 2022](https://www.cs.ucr.edu/~csong/oakland22-jigsaw.pdf)
- [FuzzUSB: Hybrid Stateful Fuzzing of USB Gadget Stacks, 2022](https://github.com/purseclab/fuzzusb/blob/main/paper/fuzzusb.pdf)
- [Effective Seed Scheduling for Fuzzing with Graph Centrality Analysis, 2022](https://arxiv.org/pdf/2203.12064.pdf)
- [BEACON : Directed Grey-Box Fuzzing with Provable Path Pruning, 2022](https://qingkaishi.github.io/public_pdfs/SP22.pdf)
- [STOCHFUZZ: Sound and Cost-effective Fuzzing of Stripped Binaries by Incremental and Stochastic Rewriting, 2021](https://www.cs.purdue.edu/homes/zhan3299/res/SP21b.pdf)
- [One Engine to Fuzz 'em All: Generic Language Processor Testing with Semantic Validation, 2021](https://huhong789.github.io/papers/polyglot-oakland2021.pdf)
- [NTFUZZ: Enabling Type-Aware Kernel Fuzzing on Windows with Static Binary Analysis, 2021](https://softsec.kaist.ac.kr/~jschoi/data/oakland2021.pdf)
- [DIFUZZRTL: Differential Fuzz Testing to Find CPU Bugs, 2021](https://lifeasageek.github.io/papers/jaewon-difuzzrtl.pdf)
- [DIANE: Identifying Fuzzing Triggers in Apps to Generate Under-constrained Inputs for IoT Devices, 2021](https://conand.me/publications/redini-diane-2021.pdf)
- [Fuzzing JavaScript Engines with Aspect-preserving Mutation, 2020](https://jakkdu.github.io/pubs/2020/park:die.pdf)
- [IJON: Exploring Deep State Spaces via Fuzzing, 2020](https://www.syssec.ruhr-uni-bochum.de/media/emma/veroeffentlichungen/2020/02/27/IJON-Oakland20.pdf)
- [Krace: Data Race Fuzzing for Kernel File Systems, 2020](https://www.cc.gatech.edu/~mxu80/pubs/xu:krace.pdf)
- [Pangolin:Incremental Hybrid Fuzzing with Polyhedral Path Abstraction, 2020](https://qingkaishi.github.io/public_pdfs/SP2020.pdf)
- [RetroWrite: Statically Instrumenting COTS Binaries for Fuzzing and Sanitization, 2020](https://www.semanticscholar.org/paper/RetroWrite%3A-Statically-Instrumenting-COTS-Binaries-Dinesh-Burow/845cafb153b0e4b9943c6d9b6a7e42c14845a0d6)
- [Full-speed Fuzzing: Reducing Fuzzing Overhead through Coverage-guided Tracing, 2019](https://www.computer.org/csdl/proceedings-article/sp/2019/666000b122/19skgbGVFEQ)
- [Fuzzing File Systems via Two-Dimensional Input Space Exploration, 2019](https://www.computer.org/csdl/proceedings-article/sp/2019/666000a594/19skfLYOpaw)
- [NEUZZ: Efficient Fuzzing with Neural Program Smoothing, 2019](https://www.computer.org/csdl/proceedings-article/sp/2019/666000a900/19skg5XghG0)
- [Razzer: Finding Kernel Race Bugs through Fuzzing, 2019](https://www.computer.org/csdl/proceedings-article/sp/2019/666000a296/19skfwZLirm)
- [Angora: Efficient Fuzzing by Principled Search, 2018](http://web.cs.ucdavis.edu/~hchen/paper/chen2018angora.pdf)
- [CollAFL: Path Sensitive Fuzzing, 2018](http://chao.100871.net/papers/oakland18.pdf)
- [T-Fuzz: fuzzing by program transformation, 2018](https://nebelwelt.net/publications/files/18Oakland.pdf)
- [Skyfire: Data-Driven Seed Generation for Fuzzing, 2017](https://www.ieee-security.org/TC/SP2017/papers/42.pdf)
- [Program-Adaptive Mutational Fuzzing, 2015](https://softsec.kaist.ac.kr/~sangkilc/papers/cha-oakland15.pdf)
- [TaintScope: A checksum-aware directed fuzzing tool for automatic software vulnerability detection, 2010](https://ieeexplore.ieee.org/abstract/document/5504701)



### USENIX Security
- [StateFuzz: System Call-Based State-Aware Linux Driver Fuzzing, 2022](https://www.usenix.org/system/files/sec22-zhao-bodong.pdf)
- [FIXREVERTER: A Realistic Bug Injection Methodology for Benchmarking Fuzz Testing, 2022](https://www.usenix.org/system/files/sec22-zhang-zenong.pdf)
- [SGXFuzz: Efficiently Synthesizing Nested Structures for SGX Enclave Fuzzing, 2022](https://www.usenix.org/system/files/sec22-cloosters.pdf)
- [AmpFuzz: Fuzzing for Amplification DDoS Vulnerabilities, 2022](https://www.usenix.org/system/files/sec22-krupp.pdf)
- [Stateful Greybox Fuzzing, 2022](https://www.usenix.org/system/files/sec22-ba.pdf)
- [BrakTooth: Causing Havoc on Bluetooth Link Manager via Directed Fuzzing, 2022](https://www.usenix.org/system/files/sec22-garbelini.pdf)
- [Fuzzing Hardware Like Software, 2022](https://www.usenix.org/system/files/sec22-trippel.pdf)
- [Drifuzz: Harvesting Bugs in Device Drivers from Golden Seeds, 2022](https://www.usenix.org/system/files/sec22-shen-zekun.pdf)
- [FuzzOrigin: Detecting UXSS vulnerabilities in Browsers through Origin Fuzzing, 2022](https://www.usenix.org/system/files/sec22-kim.pdf)
- [TheHuzz: Instruction Fuzzing of Processors Using Golden-Reference Models for Finding Software-Exploitable Vulnerabilities, 2022](https://www.usenix.org/system/files/sec22-kande.pdf)
- [MundoFuzz: Hypervisor Fuzzing with Statistical Coverage Testing and Grammar Inference, 2022](https://www.usenix.org/system/files/sec22-myung.pdf)
- [Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing, 2022](https://www.usenix.org/system/files/sec22-scharnowski.pdf)
- [SyzScope: Revealing High-Risk Security Impacts of Fuzzer-Exposed Bugs in Linux kernel, 2022](https://www.usenix.org/system/files/sec22-zou.pdf)
- [Morphuzz: Bending (Input) Space to Fuzz Virtual Devices, 2022](https://www.usenix.org/system/files/sec22-bulekov.pdf)
- [Breaking Through Binaries: Compiler-quality Instrumentation for Better Binary-only Fuzzing, 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/nagy)
- [ICSFuzz: Manipulating I/Os and Repurposing Binary Code to Enable Instrumented Fuzzing in ICS Control Applications, 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/tychalas)
- [Android SmartTVs Vulnerability Discovery via Log-Guided Fuzzing, 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/aafer)
- [Constraint-guided Directed Greybox Fuzzing, 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/lee-gwangmu)
- [Nyx: Greybox Hypervisor Fuzzing using Fast Snapshots and Affine Types, 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/schumilo)
- [UNIFUZZ: A Holistic and Pragmatic Metrics-Driven Platform for Evaluating Fuzzers, 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/li-yuwei)
- [FANS: Fuzzing Android Native System Services via Automated Interface Analysis, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/liu)
- [Analysis of DTLS Implementations Using Protocol State Fuzzing, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/fiterau-brostean)
- [EcoFuzz: Adaptive Energy-Saving Greybox Fuzzing as a Variant of the Adversarial Multi-Armed Bandit, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/yue)
- [Fuzzing Error Handling Code using Context-Sensitive Software Fault Injection, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/jiang)
- [FuzzGen: Automatic Fuzzer Generation, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/ispoglou)
- [ParmeSan: Sanitizer-guided Greybox Fuzzing, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/osterlund)
- [SpecFuzz: Bringing Spectre-type vulnerabilities to the surface, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/oleksenko)
- [FuzzGuard: Filtering out Unreachable Inputs in Directed Grey-box Fuzzing through Deep Learning, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/zong)
- [Montage: A Neural Network Language Model-Guided JavaScript Engine Fuzzer, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/lee-suyoung)
- [GREYONE: Data Flow Sensitive Fuzzing, 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/gan)
- [Fuzzification: Anti-Fuzzing Techniques, 2019](https://www.usenix.org/conference/usenixsecurity19/presentation/jung)
- [AntiFuzz: Impeding Fuzzing Audits of Binary Executables, 2019](https://www.usenix.org/conference/usenixsecurity19/presentation/guler)
- [Charm: Facilitating Dynamic Analysis of Device Drivers of Mobile Systems, 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/talebi)
- [MoonShine: Optimizing OS Fuzzer Seed Selection with Trace Distillation, 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/pailoor)
- [QSYM : A Practical Concolic Execution Engine Tailored for Hybrid Fuzzing, 2018](https://www.usenix.org/conference/usenixsecurity18/presentation/yun)
- [OSS-Fuzz - Google's continuous fuzzing service for open source software, 2017](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/serebryany)
- [kAFL: Hardware-Assisted Feedback Fuzzing for OS Kernels, 2017](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/schumilo)
- [Protocol State Fuzzing of TLS Implementations, 2015](https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/de-ruiter)
- [Optimizing Seed Selection for Fuzzing, 2014](https://softsec.kaist.ac.kr/~sangkilc/papers/rebert-usenixsec14.pdf)
- [Dowsing for overflows: a guided fuzzer to find buffer boundary violations, 2013](http://enigma.usenix.org/sites/default/files/sec13_proceedings_interior.pdf#page=57)
- [Fuzzing with Code Fragments, 2012](https://www.usenix.org/system/files/conference/usenixsecurity12/sec12-final73.pdf)


### ACM Conference on Computer and Communications Security (ACM CCS)
- [SoFi: Reflection-Augmented Fuzzing for JavaScript Engines, 2021](https://dl.acm.org/doi/pdf/10.1145/3460120.3484823)
- [T-Reqs: HTTP Request Smuggling with Differential Fuzzing, 2021](https://bahruz.me/papers/ccs2021treqs.pdf)
- [V-SHUTTLE: Scalable and Semantics-Aware Hypervisor Fuzzing, 2021](https://nesa.zju.edu.cn/download/ppt/pgn_slides_V-SHUTTLE.pdf)
- [Same Coverage, Less Bloat: Accelerating Binary-only Fuzzing with Coverage-preserving Coverage-guided Tracing, 2021](https://people.cs.vt.edu/snagy2/papers/21CCS.pdf)
- [HyperFuzzer: An Efficient Hybrid Fuzzer For Virtual CPUs, 2021](https://www.microsoft.com/en-us/research/uploads/prod/2021/09/hyperfuzzer-ccs21.pdf)
- [Regression Greybox Fuzzing, 2021](https://mboehme.github.io/paper/CCS21.pdf)
- [Hardware Support to Improve Fuzzing Performance and Precision, 2021](https://gts3.org/assets/papers/2021/ding:snap.pdf)
- [SNIPUZZ: Black-box Fuzzing of IoT Firmware via Message Snippet Inference, 2021](https://arxiv.org/pdf/2105.05445.pdf)
- [FREEDOM: Engineering a State-of-the-Art DOM Fuzzer, 2020](https://gts3.org/assets/papers/2020/xu:freedom.pdf)
- [Intriguer: Field-Level Constraint Solving for Hybrid Fuzzing, 2019](https://dl.acm.org/citation.cfm?id=3354249)
- [Learning to Fuzz from Symbolic Execution with Application to Smart Contracts, 2019](https://files.sri.inf.ethz.ch/website/papers/ccs19-ilf.pdf)
- [Matryoshka: fuzzing deeply nested branches, 2019](https://web.cs.ucdavis.edu/~hchen/paper/chen2019matryoshka.pdf)
- [Evaluating Fuzz Testing, 2018](http://www.cs.umd.edu/~mwh/papers/fuzzeval.pdf)
- [Hawkeye: Towards a Desired Directed Grey-box Fuzzer, 2018](https://chenbihuan.github.io/paper/ccs18-chen-hawkeye.pdf)
- [IMF: Inferred Model-based Fuzzer, 2017](http://daramg.gift/paper/han-ccs2017.pdf)
- [SemFuzz: Semantics-based Automatic Generation of Proof-of-Concept Exploits, 2017](https://www.informatics.indiana.edu/xw7/papers/p2139-you.pdf)
- [AFL-based Fuzzing for Java with Kelinci, 2017](https://dl.acm.org/citation.cfm?id=3138820)
- [Designing New Operating Primitives to Improve Fuzzing Performance, 2017](http://iisp.gatech.edu/sites/default/files/images/designing_new_operating_primitives_to_improve_fuzzing_performance_vt.pdf)
- [Directed Greybox Fuzzing, 2017](https://dl.acm.org/citation.cfm?id=3134020)
- [SlowFuzz: Automated Domain-Independent Detection of Algorithmic Complexity Vulnerabilities, 2017](https://arxiv.org/pdf/1708.08437.pdf)
- [DIFUZE: Interface Aware Fuzzing for Kernel Drivers, 2017](https://acmccs.github.io/papers/p2123-corinaA.pdf)
- [Systematic Fuzzing and Testing of TLS Libraries, 2016](https://www.nds.rub.de/media/nds/veroeffentlichungen/2016/10/19/tls-attacker-ccs16.pdf)
- [Coverage-based Greybox Fuzzing as Markov Chain, 2016](https://ieeexplore.ieee.org/abstract/document/8233151)
- [eFuzz: A Fuzzer for DLMS/COSEM Electricity Meters, 2016](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.817.5616&rep=rep1&type=pdf)
- [Scheduling Black-box Mutational Fuzzing, 2013](https://softsec.kaist.ac.kr/~sangkilc/papers/woo-ccs13.pdf)
- [Taming compiler fuzzers, 2013](https://www.cs.utah.edu/~regehr/papers/pldi13.pdf)
- [SAGE: whitebox fuzzing for security testing, 2012](https://dl.acm.org/citation.cfm?id=2094081)
- [Grammar-based whitebox fuzzing, 2008](https://dl.acm.org/citation.cfm?id=1375607)
- [Taint-based directed whitebox fuzzing, 2009](https://dl.acm.org/citation.cfm?id=1555061)


### ArXiv (Fuzzing with Artificial Intelligence & Machine Learning)
- [MEUZZ: Smart Seed Scheduling for Hybrid Fuzzing, 2020](https://arxiv.org/abs/2002.08568)
- [A Review of Machine Learning Applications in Fuzzing, 2019](https://arxiv.org/abs/1906.11133)
- [Evolutionary Fuzzing of Android OS Vendor System Services, 2019](https://arxiv.org/abs/1906.00621)
- [MoonLight: Effective Fuzzing with Near-Optimal Corpus Distillation, 2019](https://arxiv.org/abs/1905.13055)
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
- [Feedback-directed random test generation, 2007](https://dl.acm.org/citation.cfm?id=1248841)
- [MTF-Storm:a high performance fuzzer for Modbus/TCP, 2018](https://doi.org/10.1109/ETFA.2018.8502600)
- [A Modbus/TCP Fuzzer for testing internetworked industrial systems, 2015](https://doi.org/10.1109/ETFA.2015.7301400)



## Tools
Information about the various open source tools you can use to leverage fuzz testing.
### General-purpose
- [radamsa](https://gitlab.com/akihe/radamsa) - A general-purpose fuzzer.
- [zzuf](https://github.com/samhocevar/zzuf) - A transparent application input fuzzer.
- [FireCracker](https://github.com/blst-security/firecracker) - BLST CLI tool takes your HTTP logs, uses them to map your API flows and find risks.
### Binary
- [American Fuzzy Lop plus plus (AFL++)](https://github.com/AFLplusplus/AFLplusplus) - A superior fork to Google's AFL. more speed, more and better mutations, more and better instrumentation, custom module support, etc. [paper](https://www.usenix.org/conference/woot20/presentation/fioraldi)
- [American fuzzy lop](http://lcamtuf.coredump.cx/afl/) - A security-oriented fuzzer that employs a novel type of compile-time instrumentation and genetic algorithms to automatically discover clean, interesting test cases that trigger new internal states in the targeted binary. 
- [WinAFL](https://github.com/googleprojectzero/winafl) - A fork of AFL for fuzzing Windows binaries.
- [libFuzzer](http://llvm.org/docs/LibFuzzer.html) - A library for coverage-guided fuzz testing. [Tutorial from Google.](https://github.com/google/fuzzer-test-suite/blob/master/tutorial/libFuzzerTutorial.md)
- [Driller](https://github.com/shellphish/driller) - An implementation of the [driller paper](https://www.cs.ucsb.edu/~vigna/publications/2016_NDSS_Driller.pdf). This implementation was built on top of AFL with angr being used as a symbolic tracer.
- [shellphish fuzzer](https://github.com/shellphish/fuzzer) - A Python interface to AFL, allowing for easy injection of testcases and other functionality.
- [Eclipser](https://github.com/SoftSec-KAIST/Eclipser) - A binary-based fuzz testing tool that improves upon classic coverage-based fuzzing by leveraging a novel technique called grey-box concolic testing.
- [Jazzer](https://github.com/CodeIntelligenceTesting/jazzer) - A coverage-guided, in-process fuzzer for the Java Virtual Machine. It is based on libFuzzer and can be applied directly to compiled applications.
### Web, JavaScript
- [jsfunfuzz](https://github.com/MozillaSecurity/funfuzz) - JavaScript engine fuzzers.
- [IFuzzer](https://github.com/vspandan/IFuzzer) - An Evolutionary Interpreter Fuzzer Using Genetic Programming.
- [domato](https://github.com/googleprojectzero/domato) - DOM fuzzer from [Google Project Zero](https://github.com/googleprojectzero). [Blog Post.](https://googleprojectzero.blogspot.com/2017/09/the-great-dom-fuzz-off-of-2017.html)
- [fuzzilli](https://github.com/googleprojectzero/fuzzilli) - A (coverage-)guided Javascript engine fuzzer, written by Samuel Groß.
- [CodeAlchemist](https://github.com/SoftSec-KAIST/CodeAlchemist) - JavaScript engine fuzzer, written by KAIST SoftSec Lab.
- [test-each](https://github.com/ehmicky/test-each) - Repeat tests using different inputs.
- [gremlins.js](https://github.com/marmelab/gremlins.js) - gremlins.js is a monkey testing library written in JavaScript.
### Network protocol
- [dtls-fuzzer](https://github.com/assist-project/dtls-fuzzer) - A Java tool which performs protocol state fuzzing of DTLS servers.
- [T-Fuzz](https://github.com/HexHive/T-Fuzz) - T-Fuzz leverages a coverage guided fuzzer to generate inputs.
- [TLS-Attacker](https://github.com/RUB-NDS/TLS-Attacker) - A Java-based framework for analyzing TLS libraries.
- [DELTA](https://github.com/seungsoo-lee/DELTA) - SDN Security evaluation framework.
- [boofuzz](https://github.com/jtpereyda/boofuzz) - Network Protocol Fuzzing for Humans. Documentation is available at http://boofuzz.readthedocs.io/, including nifty quickstart guides.
- [LL-Fuzzer](https://github.com/mit-ll/LL-Fuzzer) - An automated NFC fuzzing framework for Android devices.
- [tlsfuzzer](https://github.com/tomato42/tlsfuzzer) - A SSL and TLS protocol test suite and fuzzer.
- [TumbleRF](https://github.com/riverloopsec/tumblerf) - A framework that orchestrates the application of fuzzing techniques to RF systems. 
- [PULSAR](https://github.com/hgascon/pulsar) - A method for stateful black-box fuzzing of proprietary network protocols.
- [SPIKE](https://github.com/guilhermeferreira/spikepp/tree/master/SPIKE) - A fuzzer development framework like sulley, a predecessor of sulley.
- [PROTOS](https://www.ee.oulu.fi/roles/ouspg/Protos) - Security testing of protocol implementations.
- [MTF](https://github.com/artemiosv/etfa2015) - A Modbus/TCP Fuzzer for testing internetworked industrial systems
- [MTF-Storm](https://github.com/ntinosk-mtf/etfa2018) - A high performance fuzzer for Modbus/TCP.
- [Scapy](https://github.com/secdev/scapy) - Packet manipulation program & library. Can fuzz any protocol. See the `fuzz` function.
### Driver
- [Charm](https://github.com/trusslab/charm) - A system solution that facilitates dynamic analysis of device drivers of mobile systems.
## Platform
- [certfuzz](https://github.com/CERTCC/certfuzz) - It contains the source code for the CMU CERT Basic Fuzzing Framework (BFF) and the CERT Failure Observation Engine (FOE).
- [Peach Fuzzer Platform](https://www.peach.tech/products/peach-fuzzer/) - An automated security testing platform that prevents zero day attacks by finding vulnerabilities in hardware and software systems.
- [Blackhat USA 2018 AFL workshop training materials](https://github.com/wrauner/afl-fuzzing-training) - From @wrauner at Samsung Research.
- [CI Fuzz](https://code-intelligence.com) - A CI/CD-agnostic platform for feedback-based fuzz testing of both native applications and Java web apps.

## Contribute

Contributions welcome! Read the [contribution guidelines](contributing.md) first.


## License

[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](http://creativecommons.org/publicdomain/zero/1.0)

To the extent possible under law, cpuu has waived all copyright and
related or neighboring rights to this work.
