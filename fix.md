├── .vscode 
├── additional_work 
    │ └── benchmark_evaluators_not_used 
            │ └── human_eval 
            │ ├── feature_exstraction_human_eval.txt │ ├── human_eval.py │ ├── human_eval.txt │ ├── x_code_eval.py │ ├── demo_test_code │ └── build ├── env ├── my_stackoverflow_module.egg-info ├── Pytorch Compile Time Errors Benchmark │ ├── All Python Stack Overflow Posts On The Internet │ ├── Kaggle Notebooks With Benchmark │ ├── Results │ ├── data_results.csv │ ├── data_results.xlsx │ ├── Stack Overflow Compile Time Errors │ ├── CompileTimeErrors.csv │ ├── CompileTimeErrors.xls │ ├── QueryResults1.csv │ ├── Summary of Bug Types and Composition │ ├── BugsCreated.xlsx │ ├── System Prompts for Bug Resolution │ ├── buggy_model_no_stack_trace_system_prompt.txt │ ├── code_and_stack_trace_and_potential_solution_documentation_system_prompt.txt │ ├── code_and_stack_trace_system_prompt.txt │ └── search_query_for_compile_errors.md │ ├── RAG Results │ ├── Baseline │ └── Vector Database Results ├── GPT-4O │ └── stack_overflow_test-gpt-4o.csv ├── LLAMA3 ├── 8B ├── 70B ├── Mistral-7B │ ├── mistral-7b-run1.csv │ └── mistral-7b-run1.json ├── src │ ├── pycache │ ├── octo_pack ├── not_used ├── import_fixer_prompt.txt ├── stack_overflow_search_based_on_algorithms.txt │ ├── stack_overflow_utils ├── init.py ├── process_data.py │ ├── vector_db │ ├── vector_db_4o │ ├── init.py │ ├── Create_stack_overflow_google_search.txt │ ├── feature_extraction.txt │ ├── main.py │ ├── octo_pack.py │ ├── regex_utils.py │ ├── stack_overflow_query_extract_prompt.txt ├── venv ├── .env ├── .gitignore ├── .google-cookie ├── chroma.log └── README.md └── requirements.txt └── setup.py


📦 Project Root
├── 📁 .vscode                        # VS Code settings
├── 📁 additional_work
│   └── 📁 benchmark_evaluators_not_used
│       └── 📁 human_eval             # Evaluation-related code and data (possibly experimental)
│           ├── feature_exstraction_human_eval.txt
│           ├── human_eval.py
│           ├── human_eval.txt   No
│           ├── x_code_eval.py
│           └── 📁 demo_test_code
├── 📁 build                          # (Possibly) build outputs
├── 📁 env / venv                     # Virtual environments (should only use one)
├── 📁 my_stackoverflow_module.egg-info  # Python package metadata
├── 📁 Pytorch Compile Time Errors Benchmark
│   ├── 📁 All Python Stack Overflow Posts On The Internet
│   ├── 📁 Kaggle Notebooks With Benchmark
│   ├── 📁 Stack Overflow Compile Time Errors
│   ├── 📁 Results
│   ├── 📁 Summary of Bug Types and Composition
│   ├── 📁 System Prompts for Bug Resolution
│   │   ├── buggy_model_no_stack_trace_system_prompt.txt
│   │   ├── code_and_stack_trace_and_potential_solution_documentation_system_prompt.txt
│   │   ├── code_and_stack_trace_system_prompt.txt
│   │   └── search_query_for_compile_errors.md
│   ├── 📁 RAG Results
│   ├── 📁 Baseline
│   ├── 📁 Vector Database Results
│   ├── data_results.csv
│   ├── data_results.xlsx
│   ├── CompileTimeErrors.csv
│   ├── CompileTimeErrors.xls
│   ├── QueryResults1.csv
│   ├── BugsCreated.xlsx
├── 📁 GPT-4O
│   └── stack_overflow_test-gpt-4o.csv
├── 📁 LLAMA3
├── 📁 8B
├── 📁 70B
├── 📁 Mistral-7B
│   ├── mistral-7b-run1.csv
│   └── mistral-7b-run1.json
├── 📁 src                            # Source code
│   ├── 📁 pycache                    # Python cache (can be ignored)
│   ├── 📁 octo_pack
├── 📁 not_used                       # Deprecated or unused code
├── 📁 stack_overflow_utils
│   ├── __init__.py
│   ├── process_data.py
│   ├── vector_db/
│   ├── vector_db_4o/
│   ├── main.py
│   ├── octo_pack.py
│   ├── regex_utils.py
│   ├── Create_stack_overflow_google_search.txt
│   ├── feature_extraction.txt
│   ├── stack_overflow_query_extract_prompt.txt
├── 📄 import_fixer_prompt.txt
├── 📄 stack_overflow_search_based_on_algorithms.txt
├── 📄 .env                           # Environment variable file
├── 📄 .gitignore                     # Git ignore rules
├── 📄 .google-cookie                 # Possibly auth/session cookie (be careful with this!)
├── 📄 chroma.log                     # Log file (probably from Chroma DB)
├── 📄 README.md                      # Project documentation
├── 📄 requirements.txt              # Python dependencies
└── 📄 setup.py                       # Python package setup script
