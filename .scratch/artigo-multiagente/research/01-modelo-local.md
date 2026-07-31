# Ticket 01 — Escolha do modelo local (RTX 3060 12 GB)

Label: `wayfinder:research`
Data da pesquisa: 2026-07-31
Pergunta: qual modelo de linguagem local roda numa RTX 3060 12 GB com tool calling confiável, latência representativa e reprodutibilidade?

**Convenção de evidência.**
Cada afirmação factual traz URL de fonte primária (doc oficial, código-fonte do próprio projeto, model card, paper, release notes).
Onde eu deduzi algo a partir de fontes, está marcado **[INFERÊNCIA]**.
Onde o dado não existe em fonte primária, está escrito **não encontrado** — não estimei.

Unidades: `GB` = 10^9 bytes (como o HuggingFace reporta tamanho de arquivo); `GiB` = 2^30 bytes (como `nvidia-smi` e o llama.cpp reportam memória).
A confusão entre as duas é responsável por boa parte dos erros de orçamento de VRAM, então elas estão sempre explicitadas.

---

## 1. Resumo executivo

**Os dois candidatos levantados pelo autor foram derrubados**, por motivos diferentes e ambos verificáveis.

| Candidato | Veredito | Motivo decisivo |
|---|---|---|
| `unsloth/gemma-4-12b-it-NVFP4` | **Reprovado** | NVFP4 não tem aceleração nativa em Ampere (sm_86); vLLM não roda nativamente em Windows; e este checkpoint específico nem converte para GGUF |
| `prism-ml/Bonsai-27B-gguf` (1-bit) | **Reprovado como modelo principal** | A compressão de 1 bit custa 21,6 pontos em τ²-Bench (82,90 → 61,34) — medição do próprio fabricante, exatamente na capacidade que o experimento mede |

**Recomendação:**

- **Principal — Qwen3.5-9B**, GGUF `Q6_K` (7,46 GB) ou `Q8_0` (9,53 GB), servido por `llama-server` (ou Ollama).
- **Reserva — Gemma 4 12B**, preferencialmente o **GGUF QAT de primeira parte do Google** (6,98 GB).

O Qwen3.5-9B já é o modelo configurado no repositório (`.env.example`: `OLLAMA_MODEL=qwen3.5:9b`), tem os melhores números públicos de tool calling da faixa (BFCL-V4 66,1; τ²-Bench 79,1), e cabe inteiro na placa **até em Q8_0** — o que permite rodar Q4 como operação e Q8 como controle, eliminando a quantização como variável de confusão.

**As três descobertas mais decisivas, se o autor só ler isto:**

1. **A quantização agressiva ataca exatamente a capacidade sob teste.**
   O fabricante do Bonsai mede, sob infraestrutura idêntica, que ir de FP16 para 1 bit custa 1,4 ponto em matemática e **21,6 pontos em τ²-Bench** (uso agêntico de ferramentas em múltiplos turnos). O dano não é uniforme — ele se concentra em seguimento de instrução e tool calling.

2. **Sucesso de tarefa sozinho é uma métrica cega.**
   arXiv:2607.27275 mostra que INT4 vs BF16 em τ²-bench não move o placar de sucesso (dentro de ±7,5 pts), enquanto **amplifica alucinação de nome de ferramenta em 2,5×** (649 → 1.646 eventos). O placar achatado é artefato do orçamento de retry do benchmark. Este artigo precisa reportar `valid_json@1` / `correct_function@1` / `correct_args@1` separados, ou vai medir o vazio.

3. **Robustez a formato de prompt importa mais que capacidade bruta aqui.**
   O BFCL V4 mede quanto um modelo oscila com variações de formatação de prompt. A família Qwen oscila 14-18 pontos; especialistas em function calling como o ToolACE-2-8B oscilam **81,5**. Como as duas arquiteturas comparadas necessariamente usam prompts diferentes, um modelo frágil a formato afogaria o efeito do tratamento em ruído de harness.

Detalhamento e justificativa nas seções 2 a 11. Achados sobre o próprio repositório na §12.

---

## 2. Candidato 1 — `unsloth/gemma-4-12b-it-NVFP4`

### 2.1 O repositório existe e o modelo é real

- Model card: <https://huggingface.co/unsloth/gemma-4-12b-it-NVFP4>
- Base: `google/gemma-4-12B-it`, arquitetura `Gemma4UnifiedForConditionalGeneration`, 11,95 B parâmetros, 48 camadas, contexto 256K.
  Fonte: <https://huggingface.co/unsloth/gemma-4-12b-it-NVFP4/blob/main/config.json> e o card do Google reproduzido no mesmo repo.

O `config.json` mostra que o checkpoint é **mixed-precision**, não NVFP4 puro:

- `group_0`: `format: "float-quantized"`, 8 bits, aplicado a `re:.*self_attn\.(q|k|v|o)_proj$` — ou seja, atenção em FP8.
- `group_1`: `format: "nvfp4-pack-quantized"` — MLP em NVFP4.

Esse detalhe é o que mata a conversão para GGUF (§2.4).

### 2.2 Suspeita 1 CONFIRMADA — NVFP4 só acelera em Blackwell

**FATO DOCUMENTADO.**
O PTX ISA da NVIDIA declara explicitamente as arquiteturas-alvo das instruções FP4 com block scaling:

> `.e3m2`, `.e2m3` and `.e2m1` alternate floating point type mma operation **requires sm_120a** and are supported on `sm_120f` or higher in the same family from PTX ISA version 8.8. Support for `.kind`, `.block_scale`, `.scale_vec_size` qualifier **requires sm_120a** … Qualifiers `.kind::mxf4nvf4` and `.kind::mxf4` are supported on following architectures: `sm_120a` `sm_121a`

E, para o caminho de datacenter (`tcgen05.mma`):

> Qualifiers `.kind::mxf4nvf4` and `.kind::mxf4` are supported on following architectures: `sm_100a` `sm_101a` … `sm_103a` `sm_110a`

Fonte: <https://docs.nvidia.com/cuda/parallel-thread-execution/index.html> (seções `mma` e `tcgen05.mma`, "Target ISA Notes").

A NVIDIA reforça no blog de engenharia:

> NVIDIA Blackwell fifth-generation Tensor Core architecture implements NVFP4 and can automatically handle the microscaled FP4 data …

Fonte: <https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/>

A RTX 3060 é **compute capability 8.6** (<https://developer.nvidia.com/cuda-gpus>).
Portanto: sem FP4 nativo.
E, no mesmo documento PTX, o MMA em FP8 (`.e4m3`/`.e5m2`) exige `sm_89` ou superior — **a 3060 também não tem FP8 nativo**, o que atinge o `group_0` deste checkpoint.

### 2.3 O que o vLLM faz de fato numa sm_86

**FATO DOCUMENTADO (código do próprio vLLM).**
O gate é em C++, por compute capability:

`csrc/libtorch_stable/quantization/fp4/nvfp4_scaled_mm_entry.cu`
```cpp
bool cutlass_scaled_mm_supports_fp4(int64_t cuda_device_capability) {
  ...
  if (cuda_device_capability >= 100 && cuda_device_capability < 120) return true;
  if (cuda_device_capability >= 120 && cuda_device_capability < 130) return true;
  return false;   // <-- sm_86 cai aqui
}
```
Fonte: <https://github.com/vllm-project/vllm/blob/main/csrc/libtorch_stable/quantization/fp4/nvfp4_scaled_mm_entry.cu>

Na seleção de kernel (`vllm/model_executor/kernels/linear/nvfp4/`), os três primeiros candidatos são recusados na sm_86 (`"FlashInfer cutedsl requires sm_10x"`, `"CUTLASS FP4 kernels not available"`) e o escolhido é `MarlinNvFp4LinearKernel`, cujo único gate é `has_device_capability(75)`:

`vllm/model_executor/layers/quantization/utils/marlin_utils_fp4.py`
```python
def is_fp4_marlin_supported():
    return current_platform.is_cuda() and current_platform.has_device_capability(75)
```
Fonte: <https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/layers/quantization/utils/marlin_utils_fp4.py>

**Nada quebra — e esse é justamente o perigo.**
O vLLM apenas registra um aviso e roda **weight-only W4A16** via Marlin, com ativações em BF16:

> Your GPU does not have native support for FP4 computation but FP4 quantization is being used. Weight-only FP4 compression will be used leveraging the Marlin kernel. This may degrade performance for compute-heavy workloads.

E a documentação confirma a intenção:

> On GPUs without a supported native FP4 GEMM kernel, vLLM falls back to weight-only (W4A16) execution via Marlin and logs a warning …

Fonte: <https://github.com/vllm-project/vllm/blob/main/docs/features/quantization/modelopt.md>

O grupo FP8 do checkpoint sofre rebaixamento análogo: `CompressedTensorsW8A8Fp8.get_min_capability()` retorna `89`, e `compressed_tensors.py::_get_scheme_from_parts` troca silenciosamente para `CompressedTensorsW8A16Fp8` quando o hardware não atende.
Resultado: **os dois grupos de quantização rodam weight-only via Marlin numa 3060.**

**Bug relevante a registrar:** vLLM issue #34694 relata que o Marlin NVFP4 produz saída corrompida sob `--dtype bfloat16` em GPUs sem FP4 nativo (~54,7% de zeros, similaridade de cosseno 0,22 contra referência FP32).
Fonte: <https://github.com/vllm-project/vllm/issues/34694>

### 2.4 Dois bloqueios adicionais, cada um suficiente sozinho

**(a) vLLM não roda nativamente em Windows.**

> - OS: Linux
> …
> **vLLM does not support Windows natively.** To run vLLM on Windows, you can use the Windows Subsystem for Linux (WSL) …

Fonte: <https://github.com/vllm-project/vllm/blob/main/docs/getting_started/installation/gpu.md>

Como a apresentação será gravada nessa máquina Windows, isso já elimina o caminho recomendado pelo model card.

**(b) Este checkpoint não converte para GGUF.**

O llama.cpp *tem* suporte a NVFP4 (`GGML_TYPE_NVFP4 = 40` em `ggml/include/ggml.h`) e inclusive um kernel MMQ para Ampere (`ggml/src/ggml-cuda/mmq-config-ampere.cuh`), além de suporte pleno a Gemma 4 (`LLM_ARCH_GEMMA4`, `src/models/gemma4.cpp`, e o registro `@ModelBase.register("Gemma4UnifiedForConditionalGeneration")`).
Mas o conversor rejeita configurações compressed-tensors com múltiplos grupos que não sejam todos NVFP4:

`conversion/base.py`
```python
if len(groups) > 1 and not nvfp4_compressed_tensors:
    raise NotImplementedError("Can't handle multiple config groups for compressed-tensors yet")
```
Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/conversion/base.py>

**[INFERÊNCIA]** rastreando contra o `config.json` real: `group_0.format == "float-quantized"` faz o `all(...)` retornar `False`, e `len(groups) == 2 > 1` — logo, `NotImplementedError`.

### 2.5 Penalidade quantificada

- O próprio model card: *"Do not use the Marlin backend (around 2x slower); let vLLM auto-select the NVFP4 kernel."*
  Fonte: <https://huggingface.co/unsloth/gemma-4-12b-it-NVFP4>
  **Ressalva importante:** esse "2x" compara Marlin contra o kernel NVFP4 **nativo em Blackwell**. Ele quantifica exatamente o que se perde por não ter Blackwell — não é uma medição feita em Ampere.
- Documentação e código do vLLM: *"may degrade performance for compute-heavy workloads"* — sem número.
- **Número de throughput NVFP4 vs baseline medido especificamente em Ampere: não encontrado.**

### 2.6 Veredito do candidato 1

Reprovado.
O artefato NVFP4 é o formato errado para esta placa: perde a aceleração que justifica sua existência, exige um runtime que não roda nativamente no SO do autor, e não tem caminho de conversão para o runtime que roda.

**O modelo Gemma 4 12B em si continua excelente** — só que na embalagem certa (GGUF). Ver §7 e §10.

---

## 3. Candidato 2 — `prism-ml/Bonsai-27B-gguf` (1-bit)

Esse candidato é mais interessante do que parece, e a análise precisa ser feita com cuidado: **duas das objeções óbvias contra ele estão erradas.**

### 3.1 O que é (fonte: model card)

- Derivado de `Qwen/Qwen3.6-27B`, ~27,3 B parâmetros, atenção híbrida (~75% linear / ~25% full), contexto 262K.
- Formato `GGUF Q1_0_g128`: 1 bit de sinal por peso + escala FP16 por grupo de 128 → **1,125 bits/peso reais**.
- Licença Apache 2.0.

Fonte: <https://huggingface.co/prism-ml/Bonsai-27B-gguf>

Tamanhos reais de arquivo (via API do HF, `?blobs=true`):

| Arquivo | Tamanho |
|---|---|
| `Bonsai-27B-Q1_0.gguf` | **3,80 GB** (3,53 GiB) |
| `Bonsai-27B-dspark-Q4_1.gguf` (drafter, opcional) | 1,79 GB |
| `Bonsai-27B-mmproj-Q8_0.gguf` (visão, opcional) | 0,63 GB |
| `Bonsai-27B-F16.gguf` (referência) | 53,81 GB |

### 3.2 Objeção errada nº 1: "precisa de um fork do llama.cpp"

**Falso.**
Inspecionei o cabeçalho GGUF do arquivo real (requisição HTTP com `Range: bytes=0-8000`, parse do header GGUF v3): `general.architecture = qwen35`, 851 tensores, 64 blocos, `qwen35.full_attention_interval = 4`.

A arquitetura `qwen35` **está no llama.cpp mainline**: `LLM_ARCH_QWEN35` em <https://github.com/ggml-org/llama.cpp/blob/master/src/llama-arch.cpp>.
O tipo `GGML_TYPE_Q1_0 = 41` está em `ggml/include/ggml.h`, com traits em `ggml.c` e kernels CUDA em `mmq.cuh`/`vecdotq.cuh` (caminho DP4A, disponível desde Pascal — logo, funciona em Ampere).

O próprio fabricante confirma:

> Q1_0 is supported out of the box in upstream llama.cpp across many backends: CPU (generic, NEON, and optimized x86), Metal, CUDA, and Vulkan.

| Runtime | Status |
|---|---|
| llama.cpp (CPU, Metal, CUDA, Vulkan) | ✅ Merged upstream, works out of the box |

Fonte: <https://github.com/PrismML-Eng/Bonsai-demo/blob/main/README.md>

Só a variante **ternária** (`Q2_0`) dependia do fork em CUDA — e essa dependência acabou em 2026-07-30, quando o PR "CUDA: add Q2_0 support" foi mergeado no mainline.
Fonte: <https://github.com/ggml-org/llama.cpp/pull/25707> (state: closed, merged: true, merged_at: 2026-07-30).

### 3.3 Objeção errada nº 2: "27B não cabe em 12 GB"

Para *este* modelo, cabe folgadamente. O fabricante publica a tabela de pico de memória (pesos + ativações + KV FP16 + ~1,2 GiB de overhead, somente texto):

| Modelo | Formato | Pesos | 4K ctx | 10K ctx | 100K ctx |
|---|---|---|---|---|---|
| Bonsai-27B (1-bit) | llama.cpp `Q1_0` | 3,53 GiB | 4,8 GiB | 5,2 GiB | 10,8 GiB |
| Ternary-Bonsai-27B | llama.cpp `Q2_0` | 6,66 GiB | 7,8 GiB | 8,1 GiB | 13,7 GiB |
| *referência: 27B "4-bit"* | llama.cpp `UD Q4_K_M` | 15,73 GiB | 17,2 GiB | 17,6 GiB | 23,2 GiB |

Fonte: <https://github.com/PrismML-Eng/Bonsai-demo/blob/main/README.md>

A ~8K de contexto o Bonsai-27B fica em torno de **5,0 GiB** — sobra metade da placa.

### 3.4 Existe medição real em Ampere

O repositório de demonstração publica benchmarks da comunidade com hardware identificado.
Dois deles são diretamente relevantes:

**RTX 3080 Ti 12 GB (Ampere sm_86, WSL2, Ryzen 9 5900X)** rodando Ternary-Bonsai-27B `Q2_0`, todas as camadas na GPU:

| modelo | size | backend | ngl | fa | test | t/s |
|---|---|---|---|---|---|---|
| qwen35 27B Q2_0 | 6,66 GiB | CUDA | 99 | 1 | pp512 | 1383,62 ± 24,68 |
| qwen35 27B Q2_0 | 6,66 GiB | CUDA | 99 | 1 | **tg128** | **62,98 ± 0,70** |

Fonte: <https://github.com/PrismML-Eng/Bonsai-demo/blob/main/community-benchmarks/ternary-bonsai/cuda-rtx3080ti-wsl.md>

**RTX A2000 Laptop (Ampere sm_86)** rodando Bonsai-8B `Q1_0`, GPU vs CPU — útil na §6:

| config | pp512 | tg128 |
|---|---|---|
| GPU (`-ngl 99 -fa 1`) | 1387 t/s | **63,22 t/s** |
| CPU (`-ngl 0`, 16 threads) | 1063 t/s | **21,05 t/s** |

Fonte: <https://github.com/PrismML-Eng/Bonsai-demo/blob/main/community-benchmarks/bonsai/cuda-rtxa2000-debian.md>

**[INFERÊNCIA]** A 3080 Ti tem largura de banda bem maior que a 3060 (a 3060 entrega 360 GB/s — §5.1). Como decode é limitado por banda de memória (§6.1), o número da 3060 deve ficar **abaixo** dos 62,98 t/s medidos na 3080 Ti, provavelmente na casa de 25-30 t/s. Isso é extrapolação por roofline, **não** uma medição — e não deve entrar no artigo como se fosse.

**Medição do Bonsai-27B especificamente numa RTX 3060: não encontrado.**

### 3.5 A objeção que de fato derruba o candidato: qualidade de tool calling

Esta é a descoberta decisiva do ticket, e ela vem da tabela de benchmarks do **próprio fabricante**, medida sob infraestrutura idêntica (EvalScope + vLLM em H100, thinking mode), o que a torna uma comparação interna válida — não um cruzamento entre laboratórios.

| Benchmark | Qwen3.6-27B FP16 | Bonsai-27B 1-bit | Queda relativa |
|---|---|---|---|
| MATH-500 | 99,40 | 98,00 | −1,4% |
| GSM8K | 95,30 | 92,80 | −2,6% |
| MMLU-Redux | 93,42 | 82,75 | −11,4% |
| **BFCL v3** | **77,10** | **70,72** | **−8,3%** |
| IFEval | 88,91 | 79,11 | −11,0% |
| IFBench (prompt-loose) | 68,03 | 52,36 | −23,0% |
| **τ²-Bench** | **82,90** | **61,34** | **−26,0%** |
| Média (15) | 85,07 | 76,11 | −10,5% |

Fonte: <https://huggingface.co/prism-ml/Bonsai-27B-gguf>

**O dano da compressão não é uniforme — ele se concentra exatamente onde este experimento mede.**
Matemática e código perdem 1-3%.
Seguimento de instrução e uso agêntico de ferramentas em múltiplos turnos perdem 23-26%.

τ²-Bench é precisamente a tarefa deste artigo: um agente conversando com um usuário e chamando ferramentas ao longo de vários turnos, num domínio de atendimento.
Perder 21,6 pontos absolutos nessa métrica significa que o modelo introduziria uma fonte de erro maior do que o efeito que o experimento tenta detectar.

O próprio card admite a limitação:

> **Agentic coding** (long-horizon, multi-file, run-test-and-repair workflows) is not yet a strong target of this release

### 3.6 Bloqueio operacional secundário

Não existe distribuição do Bonsai na biblioteca do Ollama (busca em <https://ollama.com/search?q=bonsai> retorna apenas modelos não relacionados).
O repositório está cabeado em Ollama (`.env.example`), então adotar o Bonsai exigiria trocar de runtime ou empacotar um Modelfile manualmente.

### 3.7 Veredito do candidato 2

Reprovado como modelo principal — por qualidade em tool calling agêntico, não por VRAM nem por runtime.

**Ressalva honesta:** o Bonsai-27B `Q1_0` é um excelente candidato a **terceiro braço opcional / análise de sensibilidade**, caso o autor queira um ponto "classe 27B" no artigo.
Ele genuinamente cabe (5,0 GiB a 8K), roda em llama.cpp mainline com binários Windows CUDA oficiais, e tem tool calling nativo OpenAI-style documentado (`--jinja`, `tool_calls` estruturados — <https://github.com/PrismML-Eng/Bonsai-demo/blob/main/TOOLS.md>).
Mas isso é escopo extra, não o eixo do experimento.

---

## 4. Suspeita 2 — "27B em GGUF Q4 passa de 12 GB?"

**CONFIRMADA para modelos 27B convencionais.**

Evidência primária direta, da biblioteca oficial do Ollama (quantização padrão das tags):

| Tag | Tamanho | Cabe em 12 GB? |
|---|---|---|
| `qwen3.6:27b` | **17 GB** | Não |
| `qwen3.5:27b` | **17 GB** | Não |
| `gemma4:26b` | 18 GB | Não |
| `gemma4:31b` | 20 GB | Não |
| `gemma4:12b` | 7,6 GB | Sim |
| `qwen3.5:9b` | 6,6 GB | Sim |

Fontes: <https://ollama.com/library/qwen3.6>, <https://ollama.com/library/qwen3.5>, <https://ollama.com/library/gemma4>

Corroborado pela tabela do card do Bonsai (§3.5): `Qwen3.6-27B Q4_K_XL` = 17,6 GB; `Gemma-4-31B QAT 4-bit` = 23,3 GB.

E por medições independentes de tamanho de arquivo em repos GGUF da geração anterior (via API do HF):

| Quant | Gemma-3-27B | Qwen3-32B |
|---|---|---|
| Q2_K | 9,78 GiB | 11,50 GiB |
| Q3_K_M | 12,52 GiB | 14,87 GiB |
| Q4_K_M | **15,41 GiB** | **18,40 GiB** |
| Q5_K_M | 17,95 GiB | 21,62 GiB |
| Q8_0 | 26,74 GiB | 32,43 GiB |

Fontes: <https://huggingface.co/bartowski/google_gemma-3-27b-it-GGUF>, <https://huggingface.co/bartowski/Qwen_Qwen3-32B-GGUF>

**Detalhe que quebra orçamentos:** o nome do quant mente.
`Q4_K_M` não são 4,0 bits/peso e sim ~4,85 — os metadados de escala/mínimo das K-quants e os tensores de embedding/saída em precisão maior somam ~20%.
Aritmética: 7.477.208.192 B × 8 ÷ 12,25e9 params = **4,88 bits/peso**.
**Orce sempre pelo tamanho de arquivo, nunca pelo nome do quant.**

### 4.1 O que a queda de quantização faz com a qualidade de tool calling

A melhor evidência primária disponível é a tabela do Bonsai (§3.5), porque ela varia **só** a quantização, mantendo modelo base, infraestrutura, decodificação e scoring idênticos.
A conclusão que ela suporta:

- Até ~4-5 bits/peso o custo é pequeno: `Qwen3.6-27B Q4_K_XL` (5,2 bpw real) marca 84,99 contra 85,07 do FP16 — **99,9%**.
- Abaixo de 3 bits o colapso é seletivo e severo: `IQ2_XXS` (2,8 bpw) cai para 72,73 (85,5%), mas de forma concentrada — 88,93 em MMLU-Redux contra 57,5 em AIME26.
  O card nomeia o risco: *"which is why casual testing misses the collapse"*.
- No regime sub-2-bit, seguimento de instrução e tool calling multi-turno são as primeiras vítimas (−23% e −26%).

**Implicação prática para o artigo:** a faixa segura é **Q5_K_M ou acima**, e o ideal é Q6_K/Q8_0 se couber — o que, para um modelo de 9B, cabe.
Ficar em Q4 num modelo grande para "caber" troca uma variável controlada (arquitetura) por uma não controlada (dano de quantização).

#### Evidência de projeto — a tabela oficial de KLD do llama.cpp

O llama.cpp publica, na doc da própria ferramenta de perplexidade, a métrica mais próxima de "o modelo vai emitir a mesma chamada de ferramenta": **same top p**, a taxa de concordância do argmax (decodificação gulosa) contra o fp16.

Llama-3-8B, WikiText-2:

| Quant | GiB | Mean KLD | **Same top p (L3-8B)** |
|---|---|---|---|
| q8_0 | 7,96 | 0,001355 | **97,674 ± 0,040%** |
| q6_K | 6,14 | 0,005452 | **96,031 ± 0,051%** |
| q5_K_M | 5,33 | 0,010762 | — |
| q4_K_M | 4,58 | 0,031273 | **91,901 ± 0,072%** |
| q3_K_M | 3,74 | 0,101913 | — |
| q2_K | 2,96 | 0,445132 | **71,138 ± 0,119%** |

Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md>

Dois pontos que essa tabela sustenta:

- **[INFERÊNCIA]** Em `Q4_K_M`, cerca de 8 tokens em 100 trocam de argmax em relação ao fp16. Uma chamada de ferramenta é uma sequência exata e longa (nome da função + chaves JSON + valores de argumento), então a probabilidade de erro **se acumula ao longo da chamada**. Em `Q8_0` são ~2,3 em 100.
- **Modelos mais novos são mais sensíveis à quantização:** no mesmo `q4_K_M`, indo de L2-7B para L3-8B, o KLD médio vai de 0,0127 para 0,0313 (2,5×) e o same-top-p cai de 94,67% para 91,90%. Extrapolar o folclore de "Q4 tá de bom tamanho" de 2023 para modelos de 2026 não é seguro.

O próprio README instrui a julgar dano por **KLD e percentis de Δp, não por perplexidade**, e avisa que PPL "is not directly comparable between models".

Nota útil: BF16 vs FP16 é essencialmente de graça (KLD médio 0,0000252; same-top-p 99,739%), então a escolha da linha de base não é confundidor.

#### Evidência acadêmica — o efeito aparece justamente onde a métrica primária não olha

**arXiv:2607.27275 — "Flat Score, Amplified Failures: How the Error Budget Masks Damage in Quantized LLM Agents"** (jul/2026).
Desenho: BF16 vs FP8 vs INT4-AWQ, vLLM em A100, **KV em 16 bits em todos os braços**, τ²-bench (Retail + Telecom), 456 episódios por célula, modelos Gemma-4-31B/26B-A4B e Qwen-3.6-27B/35B-A3B.

Achados:

- **Nenhuma diferença de sucesso de tarefa sobrevive à correção para múltiplas comparações** (limitada a ±7,5 pontos no pior caso). À primeira vista, quantizar sai de graça.
- **Não sai.** Alucinação de nome de ferramenta no Gemma-4-31B/Telecom: **649 eventos (BF16) → 1.646 (INT4)**, amplificação de 2,5×, +18,75 pontos de taxa de erro.
- Apenas 3 dos 1.646 eventos INT4 (0,18%) citam uma ferramenta que nunca foi alucinada em BF16; correlação de ranking dos modos de falha ≥ 0,94.
  **A quantização amplifica os modos de falha já existentes, em vez de criar novos.**
- O placar achatado é artefato do orçamento de erro do τ²-bench (K=10 erros recuperáveis). Reescorando: **K=10 → 1,3 pt de diferença; K=5 → 7,5 pt; K=2 → 16,7 pt.**

Corroborado por **arXiv:2409.11055**: *"quantization magnifies a model's inherent weaknesses"*; AWQ melhor que GPTQ em weight-only; modelos pequenos degradam em 4 bits enquanto 70B se mantém.

**Ressalva de transferência:** o estudo usa modelos de 26-35B com AWQ no vLLM, não 8B em GGUF Q4_K_M numa 3060. A transferência é plausível mas não testada.

**Esta é a descoberta mais importante desta seção para o desenho do artigo.**
Um experimento que reporta **apenas** sucesso de tarefa, com orçamento de retry, comprovadamente esconde uma amplificação de erro de 2,5×.

**Consequência direta para o protocolo (ticket 05):** separe as métricas.
- `valid_json@1` — a chamada é sintaticamente válida?
- `correct_function@1` — escolheu a ferramenta certa?
- `correct_args@1` — os argumentos estão certos?
- e só então sucesso de tarefa.

Um número agregado de sucesso é exatamente a instrumentação que o paper acima mostra ser cega.

#### O que continua sem fonte

**Medição de BFCL ou τ²-bench por nível de quantização GGUF (Q4_K_M vs Q5_K_M vs Q8_0 vs FP16, mesmo modelo): não encontrado.**
Nenhum paper, nenhum model card, nem a documentação da Unsloth publica isso — a Unsloth inclusive adverte: *"lower perplexity or KLD doesn't necessarily translate to better real-world performance"* (<https://unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs>).

Isso é uma lacuna real da literatura, e é barato de fechar dentro deste experimento: **rode Q4_K_M como ponto de operação e Q8_0 como controle** — ambos cabem para um modelo 9B nesta placa.
Isso transforma a escolha de quantização de suposição em resultado, e é material publicável dentro do próprio artigo.

---

## 5. Orçamento de VRAM na RTX 3060 12 GB

### 5.1 Especificações oficiais

| Spec | Valor | Fonte |
|---|---|---|
| Memória | 12 GB GDDR6 | <https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3060-3060ti/> |
| Barramento | 192-bit | idem |
| **Largura de banda** | **360 GB/s** | <https://www.nvidia.com/en-us/geforce/news/game-on-you-asked-we-answered-qa/> — *"GeForce RTX 3060 is 192-bit and GDDR6 (at 15 Gbps), delivering 360GB/s of bandwidth."* |
| Compute capability | **8.6** | <https://developer.nvidia.com/cuda-gpus> |

Conferência aritmética: 192 bits ÷ 8 = 24 B × 15 GT/s = **360 GB/s** ✓.

**Reserva de VRAM do Windows para display: não encontrado.**
A Microsoft documenta o *mecanismo* (VidMm segmenta a memória dedicada; DWM/MPO consomem parte dela — <https://learn.microsoft.com/en-us/windows-hardware/drivers/display/video-memory-management-and-gpu-scheduling>), mas **não existe declaração oficial de um valor fixo em MiB**.
Isso precisa ser **medido** com `nvidia-smi` na área de trabalho ociosa antes do experimento.

### 5.2 Teto prático

| Item | Valor | Base |
|---|---|---|
| Total da placa | 12,00 GiB | NVIDIA (12288 MiB) |
| Overhead de contexto CUDA | −0,45 GiB | Ollama `MinimumMemory()` = 457 MiB por dispositivo não-Metal, documentado em <https://github.com/ollama/ollama/blob/main/ml/device.go> |
| Reserva WDDM/DWM do Windows | **medir** | sem número oficial |
| Compute + output buffers @ 8k | −0,4 a −0,8 GiB | escala com `n_batch` e vocabulário — **[INFERÊNCIA]** |
| **Envelope prático (pesos + KV)** | **≈ 10,3-10,7 GiB** | **[INFERÊNCIA]** |

Use **10,5 GiB** como teto de trabalho e confirme contra `nvidia-smi` na máquina real.

### 5.3 Fórmula do KV cache

```
KV_bytes = 2 × n_layers × n_kv_heads × head_dim × seq_len × bytes_per_element
```
O 2 inicial = tensor K + tensor V.

Fontes primárias da fórmula:
- NVIDIA, *Mastering LLM Techniques: Inference Optimization*: *"Size of KV cache per token in bytes = 2 * (num_layers) * (num_heads * dim_head) * precision_in_bytes"* — <https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/>
- Implementação equivalente no Ollama, `GraphSize()` em <https://github.com/ollama/ollama/blob/main/fs/ggml/ggml.go>

### 5.4 KV cache dos modelos recomendados, a 8K de contexto

Ambos os modelos recomendados usam **atenção híbrida**, o que reduz o KV cache muito além do que o GQA sozinho faria. Os parâmetros vêm dos `config.json` reais.

**Qwen3.5-9B** — `num_hidden_layers=32`, `full_attention_interval=4` (logo 8 camadas full-attention, 24 lineares/DeltaNet), `num_key_value_heads=4`, `head_dim=256`.
Fonte: <https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/config.json>

```
2 × 8 camadas × 4 kv_heads × 256 head_dim × 8192 tokens × 2 B (fp16)
= 134.217.728 elementos × 2 B
= 268.435.456 B = 256 MiB = 0,25 GiB
```
As camadas Gated DeltaNet mantêm estado recorrente de tamanho fixo, independente do comprimento da sequência.

**Gemma 4 12B** — `num_hidden_layers=48`, padrão `sliding_attention` com `full_attention` a cada 6 camadas (8 globais, 40 deslizantes), `sliding_window=1024`, `num_key_value_heads=8`, `head_dim=256`.
Fonte: <https://huggingface.co/unsloth/gemma-4-12b-it-NVFP4/blob/main/config.json>

```
globais:     2 × 8  × 8 × 256 × 8192 × 2 B = 536.870.912 B = 512 MiB
deslizantes: 2 × 40 × 8 × 256 × 1024 × 2 B = 335.544.320 B = 320 MiB
total                                                        = 832 MiB = 0,81 GiB
```
Sem aproveitar a janela deslizante seriam 3,0 GiB — o llama.cpp implementa iSWA (`src/llama-kv-cache-iswa.h`), então o valor real fica próximo de 0,81 GiB, com padding de batch por cima.

### 5.5 Quantização do KV cache (llama.cpp)

Flags oficiais, de `common/arg.cpp` (<https://github.com/ggml-org/llama.cpp/blob/master/common/arg.cpp>):

- `-ctk, --cache-type-k TYPE` / `-ctv, --cache-type-v TYPE` — valores aceitos: `f32, f16, bf16, q8_0, q4_0, q4_1, iq4_nl, q5_0, q5_1`; **padrão `f16`**.
- `-fa, --flash-attn [on|off|auto]` — padrão `auto`.
- `-nkvo, --no-kv-offload`.

**Ressalva documentada:** V quantizado exige flash attention. `src/llama-context.cpp` lança erro: *"quantized V cache requires flash_attn to be enabled"*.

**Recomendação para este experimento: mantenha o KV em `f16`, e declare isso no artigo.**

Três razões, em ordem de força:

1. **Quantizar o KV é um botão separado e muito mais perigoso que quantizar pesos.**
   arXiv:2606.09864 reporta que o IFEval strict-pass despenca para **16,82% com KV cache em 6 bits**.
   Não por acaso, o estudo de agentes quantizados (arXiv:2607.27275) fixou o KV em 16 bits em **todos** os braços — justamente para não contaminar o resultado.
2. Variar quantização de peso e de KV ao mesmo tempo invalida o experimento: dois fatores, um resultado.
3. Quantizar o V força flash attention e adiciona um passo de dequantização no kernel de atenção — altera exatamente aquilo que se está medindo.

Com 9B/12B há folga de sobra (§5.6); a economia não é necessária.

### 5.6 Veredito de encaixe (8K de contexto)

| Configuração | Pesos | KV @8k | Total | Cabe? |
|---|---|---|---|---|
| **Qwen3.5-9B Q6_K** | 7,46 GB = 6,95 GiB | 0,25 GiB | **7,20 GiB** | Sim, folgado |
| **Qwen3.5-9B Q8_0** | 9,53 GB = 8,87 GiB | 0,25 GiB | **9,12 GiB** | Sim |
| **Gemma 4 12B Q4_K_M** | 7,12 GB = 6,63 GiB | 0,81 GiB | **7,44 GiB** | Sim, folgado |
| **Gemma 4 12B Q5_K_M** | 8,41 GB = 7,83 GiB | 0,81 GiB | **8,64 GiB** | Sim |
| Gemma 4 12B Q6_K | 9,79 GB = 9,12 GiB | 0,81 GiB | 9,93 GiB | Sim, apertado |
| Gemma 4 12B Q8_0 | 12,67 GB = 11,80 GiB | 0,81 GiB | 12,61 GiB | **Não** |
| Bonsai-27B Q1_0 | 3,53 GiB | ~0,5 GiB | ~5,0 GiB | Sim, muito folgado |
| Qwen3.6-27B Q4 (Ollama) | 17 GB = 15,83 GiB | — | >15,8 GiB | **Não** |

Tamanhos GGUF obtidos da API do HF (`?blobs=true`) em <https://huggingface.co/unsloth/Qwen3.5-9B-GGUF> e <https://huggingface.co/unsloth/gemma-4-12b-it-GGUF>.

**Conclusão:** a classe 27B convencional não cabe em nenhuma quantização que valha a pena medir.
A classe 9B-12B cabe com folga — e o Qwen3.5-9B cabe **até em Q8_0**, o que permite ao artigo declarar que a quantização foi praticamente eliminada como confundidor.

---

## 6. Suspeita 3 — penalidade de offload parcial para RAM

**CONFIRMADA, e a ordem de grandeza é multiplicativa, não aditiva.**

### 6.1 Princípio documentado

NVIDIA, *Mastering LLM Techniques: Inference Optimization* (<https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/>):

> [Prefill] is a matrix-matrix operation that's highly parallelized. It effectively saturates GPU utilization.

> [Decode] The speed at which the data (weights, keys, values, activations) is transferred to the GPU from memory dominates the latency, not how fast the computation actually happens. In other words, this is a **memory-bound operation**.

Logo, tempo por token de decode ≈ (bytes de peso lidos) ÷ (banda da memória onde eles estão).
Offload troca o denominador.

### 6.2 Escada de banda

| Caminho | Banda | Status |
|---|---|---|
| VRAM da RTX 3060 | **360 GB/s** | DOCUMENTADO (§5.1) |
| PCIe 4.0 x16 | 64 GB/s bidirecional (~32 GB/s por direção) | DOCUMENTADO — <https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf> |
| DDR5-5600 dual-channel | 89,6 GB/s | **[INFERÊNCIA]** aritmética: 5600 MT/s × 8 B × 2 canais |
| DDR4-3200 dual-channel | 51,2 GB/s | **[INFERÊNCIA]** aritmética |

Razões: 360÷89,6 = **4,0×** (DDR5); 360÷51,2 = **7,0×** (DDR4); 360÷32 = **11,3×** (PCIe).

### 6.3 Qual denominador se aplica depende do runtime

Este é o ponto que a maioria dos orçamentos erra:

- **llama.cpp `-ngl` parcial:** as camadas residentes em RAM são **computadas na CPU**. Os pesos não cruzam o PCIe; só vetores de ativação pequenos cruzam. Restrição = **banda DDR (4-7×)**.
- **vLLM `--cpu-offload-gb`:** os pesos são **transmitidos para a GPU a cada forward pass** via UVA. A própria doc diz: *"part of the model is loaded from CPU memory to GPU memory **on the fly in each model forward pass**"* — <https://github.com/vllm-project/vllm/blob/main/vllm/config/offload.py>. Restrição = **PCIe (11,3×)**.

### 6.4 Modelo roofline — **[INFERÊNCIA]**

Com fração `f` dos pesos na CPU:
```
razão_de_velocidade = 1 / [ (1-f) + f × (360 / BW_ram) ]
```

| f (camadas na CPU) | DDR4-3200 | DDR5-5600 |
|---|---|---|
| 5% | 0,77× (−23%) | 0,87× (−13%) |
| 10% | 0,62× (−38%) | 0,77× (−23%) |
| 25% | 0,40× (**2,5× mais lento**) | 0,57× (1,75× mais lento) |
| 50% | 0,25× (**4× mais lento**) | 0,40× (2,5× mais lento) |

Aritmética para f=0,25 em DDR4: `1 / (0,75 + 0,25 × 7,03) = 1/2,508 = 0,399`.

Isto é **inferência por roofline, não medição**. Ignora tempo de compute da CPU e overhead de lançamento/sincronização de kernel, que pioram o resultado real. Trate como limite otimista.

### 6.5 Medições primárias disponíveis

**Corroboração direta em Ampere (§3.4):** RTX A2000 sm_86 com Bonsai-8B `Q1_0` — GPU 63,22 t/s vs CPU 21,05 t/s = **3,0×**.
Esse é o caso extremo `f = 1,0` num modelo pequeno, e cai dentro da faixa prevista pelo roofline para DDR4.
Fonte: <https://github.com/PrismML-Eng/Bonsai-demo/blob/main/community-benchmarks/bonsai/cuda-rtxa2000-debian.md>

**Medição numa RTX 3060 12 GB** (llama.cpp Discussion #15396, gpt-oss-20b MXFP4, Ryzen 7 5700X):

| Config | tok/s |
|---|---|
| 2k ctx, GPU inteira | 75 |
| 16k ctx, GPU inteira | 67 |
| 16k ctx, 2 camadas MoE na CPU | 64 |
| 32k ctx, 3 camadas MoE na CPU | 56 |

Fonte: <https://github.com/ggml-org/llama.cpp/discussions/15396>

**Interpretação crítica:** esses números são de um modelo **MoE**. Um MoE lê só os especialistas ativos por token, então empurrar tensores de especialista para a CPU move poucos bytes — daí a queda suave 67→64.
**Um modelo denso de 9B/12B lê todos os pesos a cada token**, então a razão de banda DDR se aplica com força total.
Os números de MoE **não são transferíveis** para o caso denso deste experimento.

**Benchmark primário varrendo `-ngl` num modelo denso em RTX 3060: não encontrado.**
Se o autor precisar desse número, é um experimento de 10 minutos com `llama-bench -ngl <N>` — e uma medição própria vale mais que qualquer citação.

### 6.6 Consequência metodológica

Offload parcial não degrada p50/p95 suavemente — **multiplica**.
E o dano em p95 excede o dano em p50, porque camadas na CPU adicionam jitter (preempção de scheduler, contenção de DDR com outros processos) que camadas em VRAM não têm.

**Qualquer configuração com `n_gpu_layers < n_layers` invalida a comparação de latência do artigo.**

Controles a fixar explicitamente:
- llama.cpp: `-ngl` com o número exato de camadas. O padrão é `auto` (<https://github.com/ggml-org/llama.cpp/blob/master/common/arg.cpp>), que **silenciosamente** faz offload em vez de falhar.
- Ollama: `num_gpu`, cujo padrão é `-1` = "set dynamically" (<https://github.com/ollama/ollama/blob/main/api/types.go>). O escalonador calcula `available := gpu.FreeMemory - envconfig.GpuOverhead() - gpu.MinimumMemory()` (<https://github.com/ollama/ollama/blob/main/server/sched.go>).

**Verificação obrigatória antes de gravar qualquer medição:** ler o log de inicialização do llama.cpp e confirmar que todas as camadas foram atribuídas a `CUDA0`, e registrar os `compute buffer size` / `output buffer size` impressos.

---

## 7. Tool calling: o que cada runtime suporta

### 7.1 llama.cpp (`llama-server`)

**Suporte universal, documentado.**

> [chat.h] adds support for OpenAI-style function calling and is used in: `llama-server` when started w/ `--jinja` flag
>
> Function calling is supported for all models … Native tool call formats supported: Llama 3.1/3.3, Functionary v3.1/v3.2, Hermes 2/3, Qwen 2.5, Qwen 2.5 Coder, Mistral Nemo, Firefunction v2, Command R7B, DeepSeek R1 …
>
> Generic tool call is supported when the template isn't recognized by native format handlers (you'll see `Chat format: Generic` in the logs).

Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md>

O README do servidor confirma a flag e o override de template:

> OpenAI-style function calling is supported with the `--jinja` flag (and may require a `--chat-template-file` override …)

Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md>

**Diferencial importante para este experimento — decodificação restrita por gramática.**
O código atual usa parsers PEG por família de modelo, incluindo um dedicado ao Gemma 4:

`common/chat.h`
```cpp
enum common_chat_format {
    COMMON_CHAT_FORMAT_CONTENT_ONLY,
    COMMON_CHAT_FORMAT_PEG_SIMPLE,
    COMMON_CHAT_FORMAT_PEG_NATIVE,
    COMMON_CHAT_FORMAT_PEG_GEMMA4,
    COMMON_CHAT_FORMAT_PEG_MINIMAX_M3,
    ...
};
```

E `tool_choice` é suportado nos três modos, com `required` forçando pelo menos uma chamada:

`common/chat.cpp`
```cpp
if (tool_choice == "auto")     return COMMON_CHAT_TOOL_CHOICE_AUTO;
if (tool_choice == "none")     return COMMON_CHAT_TOOL_CHOICE_NONE;
if (tool_choice == "required") return COMMON_CHAT_TOOL_CHOICE_REQUIRED;
...
auto min_calls = inputs.tool_choice == COMMON_CHAT_TOOL_CHOICE_REQUIRED ? 1 : 0;
```
Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/common/chat.cpp>

Isso importa porque **elimina a classe de falha "o modelo emitiu JSON malformado"** — a gramática impede sintaticamente. O que sobra de erro é escolha errada de ferramenta ou de argumento, que é o que o experimento *quer* medir.

**Nota de procedência:** o suporte a `tool_choice: required` está no **código-fonte** (`common/chat.cpp`, acima), mas **não está descrito na documentação** de function calling nem no README do servidor.
Se o artigo depender desse comportamento, valide empiricamente na build usada em vez de citar a doc.

Paralelismo: `"parallel_tool_calls": true` no payload (desabilitado por padrão).

### 7.2 Ollama

**Suportado e documentado em `/api/chat`:**

> `tools`: list of tools in JSON for the model to use if supported
>
> `tool_calls` (optional): a list of tools in JSON that the model wants to use
>
> Tool calling is supported by providing a list of tools in the `tools` parameter.

Fonte: <https://github.com/ollama/ollama/blob/main/docs/api.md>

Há exemplos documentados de tool calling com e sem streaming (`Chat request (Streaming with tools)`, `Chat request (No streaming, with tools)`).

**Saídas estruturadas** (útil como cinto de segurança adicional):

> `format`: the format to return a response in. Format can be `json` or a JSON schema
>
> Structured outputs are supported by providing a JSON schema in the `format` parameter.

Quais modelos suportam: o Ollama sinaliza por *capability badge* na página da biblioteca.
Verificado nesta pesquisa:

| Modelo | Badges | URL |
|---|---|---|
| `qwen3.5` | `vision`, `tools`, `thinking` | <https://ollama.com/library/qwen3.5> |
| `gemma4` | `vision`, `tools`, `thinking` (+ `audio`) | <https://ollama.com/library/gemma4> |
| `qwen3.6` | `vision`, `tools`, `thinking` | <https://ollama.com/library/qwen3.6> |
| `granite4.1` | `tools` | <https://ollama.com/library/granite4.1> |
| `ministral-3` | `vision`, `tools` | <https://ollama.com/library/ministral-3> |
| `gemma3` | **sem `tools`** | <https://ollama.com/library/gemma3> |

O mecanismo por trás do badge é o template: *"Tools support can be added to a model by adding a `{{ .Tools }}` node to the template."*
Fonte: <https://github.com/ollama/ollama/blob/main/docs/template.mdx>
Ou seja, "suporta tools" no Ollama significa "o template Go empacotado referencia `.Tools`/`.ToolCalls`" — não é uma medição de qualidade.

**Limitação importante do Ollama: `tool_choice` não é suportado.**
No endpoint nativo `/api/chat` o campo não existe, e na própria lista de compatibilidade OpenAI do Ollama ele aparece como item **não** implementado (`- [ ] tool_choice`).
Fonte: <https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx>

Isso é uma assimetria concreta contra o llama.cpp e o vLLM: **não dá para forçar uma chamada de ferramenta no Ollama.**
Se o desenho do braço B depender de forçar a chamada, o Ollama não serve.

### 7.3 vLLM

Suporta tool calling com `--enable-auto-tool-choice` e `--tool-call-parser <parser>`.
O próprio model card do Qwen3.5-9B documenta o comando exato:

```shell
vllm serve Qwen/Qwen3.5-9B --port 8000 --tensor-parallel-size 1 --max-model-len 262144 \
  --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_coder
```
Fonte: <https://huggingface.co/Qwen/Qwen3.5-9B>

**Mas o vLLM está fora deste experimento** por não rodar nativamente em Windows (§2.4a).
Fica registrado apenas para completude e para eventual replicação em Linux.

### 7.4 Descoberta crítica no repositório: o prefixo do LiteLLM está errado

`shared/infrastructure/llm.py` monta o modelo como:

```python
if provider == "ollama":
    return f"ollama/{cfg.ollama_model}"
```

A documentação do LiteLLM é explícita:

> In order to send ollama requests to `POST /api/chat` on your ollama server, set the model prefix to `ollama_chat`
>
> We recommend using `ollama_chat` for better responses.

E o exemplo de tool calling usa justamente esse prefixo: `completion(model="ollama_chat/llama3.1", messages=messages, tools=tools)`, com a ressalva:

> not all ollama models support function calling, litellm defaults to json mode tool calls if native tool calling not supported

Fonte: <https://docs.litellm.ai/docs/providers/ollama>

**Ou seja:** o prefixo `ollama/` roteia para `/api/generate` (completion), não para `/api/chat` — que é o endpoint que aceita `tools` e devolve `tool_calls`.
Para o braço B (agente único com tool calling) funcionar, o prefixo precisa virar `ollama_chat/`.

O código do LiteLLM confirma o repasse nativo: `litellm/llms/ollama/chat/transformation.py` lista `"tools"` em `get_supported_openai_params`, com o comentário `# Ollama 0.4+ supports native tool calling - pass tools directly`, e define `finish_reason = "tool_calls"`.

**Não existe provider `llamacpp` no LiteLLM.**
Verificado contra o enum `LlmProviders` em `litellm/types/utils.py`: existem `OLLAMA_CHAT = "ollama_chat"` e `HOSTED_VLLM = "hosted_vllm"`, sem entrada para llama.cpp.
O caminho documentado é tratá-lo como endpoint OpenAI-compatível:

```python
completion(model="openai/<nome>", api_base="http://localhost:8080/v1", api_key="sk-noop", ...)
```
Fonte: <https://docs.litellm.ai/docs/providers/openai_compatible>

### 7.5 Armadilha a checar antes de culpar o modelo

**arXiv:2606.25605** relata que, com `tools` ligado **e** um schema de resposta estruturada ligado ao mesmo tempo, a taxa de invocação de ferramenta cai para **0%** em vários modelos abertos testados (incluindo Qwen3.6-35B-A3B, Qwen3.5-122B-A10B e GPT-OSS-20B).
A correção documentada é dividir em dois passos: passo 1 com tools e sem schema; passo 2 com schema.
O relato é de 0% → 100% com a divisão.

**Verifique isso antes de atribuir qualquer falha de tool calling ao modelo ou à quantização.**
Vale especialmente aqui, porque o Ollama oferece `format` (JSON schema) e é tentador ligá-lo "por segurança" junto com `tools`.

### 7.6 O outro lado: decodificação restrita não conserta semântica

Vale registrar o limite, para o artigo não superestimar o ganho da gramática:

- **Sintaxe: resolvida por construção.** A máscara de gramática (GBNF no llama.cpp, xgrammar/llguidance no vLLM, `format` no Ollama) atua sobre o vetor de logits depois do forward pass. A quantização perturba os logits, não a máscara. **[INFERÊNCIA]** a partir da documentação, não é resultado medido.
- **Semântica: não resolvida, e o custo aparece em outro lugar.** arXiv:2605.26128 mediu, numa tarefa de chamada de ferramenta de calendário, **validade de schema em 100% nos dois braços enquanto a acurácia executável caiu de 91,5% para 48,0%** (−43,5 pontos). Em outro cenário, a validade subiu 38,5 pontos e a taxa de "válido porém errado" subiu 39,4 pontos.
  **O erro mudou de forma; não desapareceu.**

**Síntese [INFERÊNCIA]:** decodificação restrita provavelmente torna o nível de quantização irrelevante para `valid_json@1` e totalmente relevante para `correct_function@1` / `correct_args@1` — porque o dano da quantização se concentra em alucinação de nome de ferramenta e erro de argumento (arXiv:2607.27275), classe que a gramática só cobre se enumerar os nomes legais de ferramenta como um `enum` explícito.
Isso não está testado na literatura, e é outro achado barato que este experimento pode produzir.

**Consequência de desenho:** decodificação restrita é uma **segunda variável independente**.
Ligá-la só no braço B confunde tudo. Ou liga nos dois, ou desliga nos dois, ou vira fator declarado.

---

## 8. Alternativas na faixa 7B-14B com tool calling comprovado

### 8.1 Qwen3.5-9B — **a mais forte, e já é o modelo do repositório**

- Repo: <https://huggingface.co/Qwen/Qwen3.5-9B> (Apache 2.0)
- 9B parâmetros, 32 camadas, arquitetura híbrida Gated DeltaNet + Gated Attention, contexto nativo 262.144 tokens, 201 idiomas.
- Ollama: `qwen3.5:9b`, 6,6 GB, badges `vision`/`tools`/`thinking` — <https://ollama.com/library/qwen3.5>
- GGUF com todos os níveis: <https://huggingface.co/unsloth/Qwen3.5-9B-GGUF>

**Evidência de qualidade em tool calling — tabela do próprio model card**, colunas na ordem GPT-OSS-120B / GPT-OSS-20B / Qwen3-Next-80B-A3B-Thinking / Qwen3-30BA3B-Thinking-2507 / **Qwen3.5-9B** / Qwen3.5-4B:

| Benchmark | Qwen3-Next-80B | Qwen3-30BA3B | **Qwen3.5-9B** | Qwen3.5-4B |
|---|---|---|---|---|
| **BFCL-V4** | 49,7 | 42,4 | **66,1** | 50,3 |
| **TAU2-Bench** | 57,4 | 41,9 | **79,1** | 79,9 |
| VITA-Bench | 29,5 | 14,1 | **29,8** | 22,0 |
| DeepPlanning | 0,4 | 4,9 | **18,0** | 17,6 |

Fonte: <https://huggingface.co/Qwen/Qwen3.5-9B>

O card também documenta a metodologia do τ²: *"TAU2-Bench: we follow the official setup except for the airline domain, where all models are evaluated by applying the fixes proposed in the Claude Opus 4.5 system card."*

**Ressalva de leitura:** o Qwen3.5-4B marca 79,9 em TAU2, ligeiramente acima do 9B (79,1).
Uma inversão dessas é sinal de que tabelas de fabricante têm ruído e/ou configurações não idênticas entre linhas — cite os números, mas não construa argumento em cima de diferenças de menos de ~2 pontos.

### 8.2 Gemma 4 12B Unified — a melhor reserva

- Card (via Unsloth, com o card do Google reproduzido): <https://huggingface.co/unsloth/gemma-4-12b-it-GGUF>
- 11,95 B parâmetros, 48 camadas, contexto 256K, licença Apache 2.0, arquitetura encoder-free.
- Ollama: `gemma4:12b`, 7,6 GB, badge `tools` — <https://ollama.com/library/gemma4>

**Evidência de tool calling — tabela oficial do Google:**

| Benchmark | Gemma 4 31B | Gemma 4 26B A4B | **Gemma 4 12B Unified** | Gemma 4 E4B |
|---|---|---|---|---|
| **Tau2 (média de 3)** | 76,9% | 68,2% | **69,0%** | 42,2% |
| MMLU Pro | 85,2% | 82,6% | 77,2% | 69,4% |
| BigBench Extra Hard | 74,4% | 64,8% | 53,0% | 33,1% |

E, nas capacidades declaradas:

> **Function Calling** – Native support for structured tool use, enabling agentic workflows.
> **Multilingual** – Out-of-the-box support for 35+ languages, pre-trained on 140+ languages.

**Vantagem específica:** o llama.cpp tem um parser de tool call *dedicado* ao Gemma 4 (`COMMON_CHAT_FORMAT_PEG_GEMMA4`, com regras de gramática próprias em `common/chat.cpp`), o que dá a essa família o caminho de parsing mais bem testado do runtime.

### 8.3 Comparação direta dos três, na métrica que importa

| Modelo | τ²-Bench | BFCL | Cabe em 12 GB? | Fonte da medição |
|---|---|---|---|---|
| **Qwen3.5-9B** | **79,1** | 66,1 (V4) | Sim, até Q8_0 | Qwen (bf16) |
| **Gemma 4 12B** | **69,0** | não publicado | Sim, até Q6_K | Google |
| Bonsai-27B 1-bit | **61,34** | 70,72 (v3) | Sim, folgado | Prism ML |
| *(referência)* Qwen3.6-27B FP16 | 82,90 | 77,10 (v3) | **Não** | Prism ML |

**Ressalva metodológica obrigatória:** as três primeiras linhas vêm de laboratórios diferentes, com harnesses e configurações possivelmente distintas. τ²-Bench e BFCL têm versões diferentes entre elas (BFCL V4 vs v3).
**Comparação cruzada entre fabricantes é evidência direcional, não medição controlada.**
A única comparação interna válida da tabela é Bonsai-27B 1-bit vs Qwen3.6-27B FP16 (mesmo laboratório, mesma infraestrutura).

### 8.4 Estado do BFCL — dados oficiais

Página: <https://gorilla.cs.berkeley.edu/leaderboard.html> · repo: <https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard>

A tabela HTML é renderizada por JavaScript, mas os CSVs que ela consome são acessíveis diretamente e são **a fonte primária citável**:

- <https://gorilla.cs.berkeley.edu/data_overall.csv> (109 modelos)
- também `data_live`, `data_non_live`, `data_multi_turn`, `data_agentic`, `data_format_sensitivity`

**Versão corrente: BFCL V4.** Evolução: v1 (simple/parallel/multiple AST) → v2 (live/enterprise) → v3 (multi-turn) → **v4 acrescenta busca web agêntica, gestão de memória agêntica e sensibilidade a formato**.
`Overall Acc` é média não-ponderada das subcategorias; categoria não avaliada conta como 0.

**Ressalva crítica de data:** os seis CSVs têm `Last-Modified: Mon, 13 Apr 2026`.
**O quadro oficial está congelado em abril de 2026** — por isso Qwen3.5, Granite 4.1 e Gemma 4 não aparecem nele.
Qualquer número "atual" de BFCL para esses modelos é **auto-reportado pelo fabricante**, não verificado pelo Berkeley.
Registre a data de acesso e essa limitação se o artigo citar o leaderboard.

Topo geral: Claude-Opus-4-5 **77,47%**. Melhor peso-aberto: GLM-4.6 (FC thinking) **72,38%**.

**Melhores modelos abertos ≤14B no quadro oficial V4:**

| Modelo | Overall | Non-Live AST | Live | Multi-Turn | Licença |
|---|---|---|---|---|---|
| Nanbeige4-3B-Thinking-2511 (FC) | **51,40%** | 81,58 | 79,42 | 51,12 | apache-2.0 |
| xLAM-2-8b-fc-r (FC) | **46,68%** | 84,58 | 67,95 | **70,00** | cc-by-nc-4.0 |
| BitAgent-Bounty-8B | 46,23% | 81,60 | **93,12** | 62,38 | Apache-2.0 |
| Qwen3-8B (FC) | 42,57% | 87,58 | 80,53 | 41,75 | apache-2.0 |
| ToolACE-2-8B (FC) | 42,44% | 87,10 | 77,42 | 38,38 | Apache-2.0 |
| Qwen3-14B (FC) | 41,03% | 84,94 | 80,01 | 34,75 | apache-2.0 |
| Gemma-3-12b-it (Prompt) | 30,43% | 79,44 | 74,24 | 5,75 | gemma-terms |
| Granite-3.2-8B-Instruct (FC) | 26,87% | 79,77 | 60,33 | 7,38 | Apache-2.0 |
| Llama-3.1-8B-Instruct (Prompt) | 25,83% | 84,00 | 70,76 | 11,12 | Llama 3 Comm. |

Nota de leitura: **Qwen3-8B supera Qwen3-14B** (42,57 vs 41,03). Maior não é melhor nesta métrica.
E a linha do Ministral-8B-2410 (11,10%, com 0,00 em todas as categorias AST/live/multi-turn) é uma **execução de avaliação quebrada**, não uma medição de capacidade — não use como evidência contra a Mistral.

### 8.5 O achado do BFCL que mais importa para um experimento controlado

O V4 acrescentou **sensibilidade a formato**: 26 variações de formato de prompt (formato de retorno Python/JSON/XML, formato da doc, tags `<TOOLCALL>`, texto puro vs Markdown, estilo de prompt) sobre 200 entradas de turno único.
`Max Delta` = diferença entre o melhor e o pior formato. **Menor é melhor.**

Fonte: <https://gorilla.cs.berkeley.edu/data_format_sensitivity.csv>

| Modelo | Max Delta | Desvio padrão |
|---|---|---|
| **Qwen3-14B (Prompt)** | **14,0** | 3,97 |
| **Qwen3-32B (Prompt)** | 15,5 | 3,75 |
| **Qwen3-30B-A3B-2507 (Prompt)** | 16,0 | 4,13 |
| **Qwen3-8B (Prompt)** | 16,5 | 5,09 |
| **Qwen3-4B-2507 (Prompt)** | 18,0 | 5,22 |
| Gemma-3-27b-it | 34,0 | 8,06 |
| Mistral-Small-2506 | 50,0 | 13,57 |
| Gemma-3-12b-it | 67,5 | 22,41 |
| Llama-3.1-8B-Instruct | 74,5 | 29,1 |
| Phi-4 | 81,5 | 23,34 |
| **ToolACE-2-8B (FC)** | **81,5** | 27,92 |
| CoALM-8B | 79,0 | 34,18 |

**Duas conclusões, e a segunda é contraintuitiva:**

1. **A família Qwen é, de longe, a mais robusta a formato de prompt** — todo o grupo entre 14 e 18, enquanto o resto do quadro fica entre 34 e 81.
2. **Os fine-tunes especializados em function calling são os modelos MAIS frágeis a formato do quadro.** ToolACE-2-8B oscila 81,5 pontos dependendo de como o prompt é formatado.

Para este experimento em particular, isso é decisivo.
A variável manipulada é a **arquitetura de orquestração** — e as duas arquiteturas necessariamente formatam o prompt de forma diferente (o supervisor tem prompt e conjunto de ferramentas diferentes do agente único).
**Um modelo que se move 80 pontos com formatação de prompt afogaria o efeito do tratamento em ruído de harness.**

Este é o argumento mais forte a favor da linha Qwen sobre qualquer especialista em FC, e vale mais do que alguns pontos de BFCL bruto.

### 8.6 Outras opções verificadas

**`ibm-granite/granite-4.1-8b`** — <https://huggingface.co/ibm-granite/granite-4.1-8b>, Apache 2.0, 8B denso, 40 camadas, contexto 131.072.
**BFCL v3 = 68,27** publicado na tabela de avaliação do próprio card (3B: 60,80; 30B: 73,68 — uma escada de escala limpa, se o autor quiser um segundo eixo).
Ollama `granite4.1` com badge `tools` (`8b-q4_K_M` 5,3 GB; `8b-q8_0` 9,3 GB). Parser dedicado no vLLM: `--tool-call-parser granite4`.
*Ponto forte:* é arquitetonicamente **não relacionado** ao Qwen — um resultado que se sustenta nos dois não é artefato do Qwen.
*Ponto fraco:* atenção full em todas as 40 camadas, então o KV cache é grande (~1,34 GiB a 8K, 5,37 GiB a 32K) — na prática limita o contexto a 8K-16K nesta placa.
Nota: o repo `granite-4.1-8b-instruct` **não existe**; o id correto é sem sufixo.

**`Salesforce/Llama-xLAM-2-8b-fc-r`** — <https://huggingface.co/Salesforce/Llama-xLAM-2-8b-fc-r>.
Único ≤14B com evidência forte de **duas** origens independentes: quadro oficial BFCL V4 (46,68%, e o **melhor multi-turn de qualquer modelo ≤14B: 70,00**) e paper revisado (APIGen-MT, arXiv:2504.03601: BFCL v3 **72,83**, tau-bench 46,7).
GGUF de primeira parte: <https://huggingface.co/Salesforce/Llama-xLAM-2-8b-fc-r-gguf> (Q4_K_M 4,92 GB).
**Bloqueio para este caso:** licença `cc-by-nc-4.0` (não comercial — aceitável academicamente, mas registre), **não está na biblioteca oficial do Ollama**, e seus primos arquiteturais (ToolACE-2, CoALM) são os mais frágeis a formato do quadro (§8.5).

**`Qwen/Qwen3.5-4B`** — <https://huggingface.co/Qwen/Qwen3.5-4B>, Apache 2.0, mesma arquitetura híbrida, 262K de contexto.
BFCL-V4 **50,3** · TAU2-Bench **79,9** · VITA 22,0 · DeepPlanning 17,6.
Ollama `qwen3.5:4b`: q4_K_M 3,4 GB, q8_0 5,3 GB, **bf16 9,3 GB**.

**Valor metodológico específico: o BF16 de 9,3 GB cabe na placa.**
É a única opção da lista que roda **completamente sem quantização** em 12 GB.
Dado que ninguém publicou BFCL por nível de quant GGUF (§4.1), um braço com quantização eliminada como confundidor vale mais para o artigo do que a diferença bruta de capacidade contra o 9B.

**Descartados após verificação:** Qwen3-14B (não cabe: 9,3 GB de pesos + 5,37 GiB de KV a 32K = 14,7 GB); Hermes-4-14B (sem benchmark de tool calling, `ollama.com/library/hermes4` → 404); LoopTool-8B (melhores números ≤14B que encontrei — BFCL v3 74,93, arXiv:2511.09148 — mas 13 downloads, sem GGUF, fora do Ollama: artefato de pesquisa, não implantável); Nanbeige4-3B e BitAgent-Bounty-8B (topo do quadro mas sem presença no Ollama e, no segundo caso, README vazio); Mistral Small/Devstral/Magistral (24B, fora da faixa); Qwen3.5-35B-A3B (BFCL-V4 67,3, mas 20-24 GB — não cabe).

### 8.7 Nota sobre vLLM em Ampere, para registro

Caso o experimento seja replicado em Linux, a matriz oficial de quantização do vLLM importa:
AWQ ✅, GPTQ ✅, Marlin ✅, INT8 W8A8 ✅, bitsandbytes ✅, GGUF ✅, **FP8 W8A8 ❌**.

> FP8 computation is supported on NVIDIA GPUs with compute capability >= 8.9 (Ada Lovelace, Hopper). FP8 models will run on compute capability >= 7.5 (Turing) as weight-only W8A16, utilizing FP8 Marlin.

Fonte: <https://github.com/vllm-project/vllm/blob/main/docs/features/quantization/README.md>

Numa 3060, os braços reais em vLLM são **AWQ ou GPTQ W4A16**.

---

## 9. Reprodutibilidade — como fixar seed e temperatura

Requisito do artigo. As três informações abaixo são documentadas.

### 9.1 Ollama

A doc traz uma seção intitulada **"Request (Reproducible outputs)"**:

> For reproducible outputs, set `seed` to a number:

```shell
curl http://localhost:11434/api/generate -d '{
  "model": "...",
  "options": { "seed": 123 }
}'
```
Fonte: <https://github.com/ollama/ollama/blob/main/docs/api.md>

`temperature` vai no mesmo objeto `options`. Para o experimento: `"options": {"seed": <fixo>, "temperature": 0, "num_ctx": 8192, "num_gpu": <todas as camadas>}`.

`num_ctx` precisa ser explícito — o padrão do Ollama é menor que o do modelo, e mudá-lo entre execuções muda a alocação de KV e a latência.

Documentação adicional do `PARAMETER` no Modelfile (<https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx>): `seed` — *"Sets the random number seed to use for generation. Setting this to a specific number will make the model generate the same text for the same prompt. (Default: 0)"*; `temperature` (padrão 0.8), `top_k` (40), `top_p` (0.9), `num_predict` (-1).

### 9.2 llama.cpp

- Flag de servidor: `-s, --seed SEED` — *"RNG seed (default: -1, use random seed for -1)"*.
- **Por requisição:** o corpo aceita `seed` — *"`seed`: Set the random number generator (RNG) seed. Default: `-1`, which is a random seed."*
- Decodificação gulosa: `temp <= 0` → argmax. Fonte no código: `llama_sampler_temp_impl` em <https://github.com/ggml-org/llama.cpp/blob/master/src/llama-sampler.cpp> (`if (temp <= 0.0f) { // find the token with the highest logit and set the rest to -inf`).

Fonte das flags: <https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md>

Seed por requisição é superior a seed por servidor para este desenho: permite fixar a semente **por caso de teste**, tornando cada célula da matriz (caso × braço × repetição) reproduzível isoladamente, sem depender da ordem de execução.

**Armadilha 1 — os defaults de amostragem do llama.cpp NÃO são neutros.**
`--temp 0.80`, `--top-k 40`, `--top-p 0.95` e `min-p 0.05` estão **ativos** a menos que sobrescritos.
Definir apenas `temperature: 0` e assumir que o resto está desligado é erro comum. Sobrescreva explicitamente.

**Armadilha 2 — `cache_prompt` é `true` por padrão e é uma fonte documentada de não-determinismo.**
Esta é a citação mais importante desta seção para o artigo:

> Because (depending on the backend) the logits are **not** guaranteed to be bit-for-bit identical for different batch sizes (prompt processing vs. token generation) enabling this option can cause nondeterministic results. Default: `true`

Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md> (opção `cache_prompt`)

**[INFERÊNCIA]** Como o padrão é `true`, envie `"cache_prompt": false` nas execuções medidas. A doc declara o risco; ela não prescreve a configuração.

Note a tensão de desenho aqui: desligar `cache_prompt` melhora a reprodutibilidade **e** neutraliza a vantagem artificial de cache de prefixo do braço multi-agente (§10.2) — os dois objetivos apontam para a mesma configuração.

### 9.3 vLLM (para eventual replicação em Linux)

É o único dos três com página oficial de reprodutibilidade — <https://docs.vllm.ai/en/latest/usage/reproducibility.html>:

> vLLM does not guarantee the reproducibility of the results by default, for the sake of performance. To achieve reproducible results:
> - In offline mode, you can either set `VLLM_ENABLE_V1_MULTIPROCESSING=0` which makes scheduling deterministic, or enable batch invariance …
> - In online mode, you can only enable batch invariance.
>
> Even with the above settings, vLLM only provides reproducibility when it runs **on the same hardware and the same vLLM version**.

E há um interruptor dedicado, `VLLM_BATCH_INVARIANT=1` (<https://docs.vllm.ai/en/latest/features/batch_invariance.html>), que exige *"NVIDIA GPUs with compute capability 8.0 or higher"* — a 3060 (8.6) qualifica.
Status: **beta**, com custo de desempenho declarado como intencional.

### 9.4 Limite honesto a declarar no artigo

`temperature = 0` torna a amostragem determinística, mas **não** garante reprodutibilidade bit-a-bit em GPU: a ordem de redução em kernels paralelos e o tamanho de batch alteram os últimos bits dos logits e podem virar um empate entre tokens.
Isso não é especulação — é o que a doc do llama.cpp declara (§9.2) e o que a doc do vLLM declara (§9.3).

O PyTorch documenta o mesmo princípio de forma geral:

> Completely reproducible results are not guaranteed across PyTorch releases, individual commits, or different platforms. Furthermore, results may not be reproducible between CPU and GPU executions, even when using identical seeds.

Fonte: <https://docs.pytorch.org/docs/stable/notes/randomness.html>

**Declaração oficial de garantia de determinismo bit-a-bit do Ollama: não encontrado.**
O texto documentado diz "reproducible outputs" e "will make the model generate the same text for the same prompt" — não "bit-identical", e sem ressalva de hardware/batching.

**Mitigação prática e verificável, em ordem:**

1. Fixar `seed` e `temperature=0`, **e sobrescrever explicitamente `top_k`, `top_p` e `min_p`** (não confie nos defaults).
2. Enviar `"cache_prompt": false` (llama.cpp).
3. Rodar **uma sequência por vez**, sem concorrência — o que este experimento precisa fazer de qualquer forma, já que mede latência.
4. Rodar cada célula **N vezes** e **reportar a variação observada**. Se houver divergência, ela vira um número no artigo em vez de uma suposição. Esta é a única forma honesta de tratar o assunto.
5. Registrar a build exata do runtime (ex.: llama.cpp `b10201`, <https://github.com/ggml-org/llama.cpp/releases>) ou a versão do Ollama, mais o digest da tag do modelo.

Para o texto do artigo: reporte seed + temperatura + a **ressalva de determinismo do runtime citada literalmente**, em vez de afirmar reprodução exata.

---

## 10. Instrumentação de tokens e latência (cliente Python)

### 10.1 Estado atual do repositório — duas lacunas bloqueantes

**Lacuna 1 — `llm_completion()` descarta `tool_calls`.**
`shared/infrastructure/llm.py` retorna apenas:

```python
return {
    "content": response.choices[0].message.content or "",
    "tokens_in": response.usage.prompt_tokens if response.usage else 0,
    "tokens_out": response.usage.completion_tokens if response.usage else 0,
    "model": response.model,
}
```

Não há leitura de `response.choices[0].message.tool_calls`.
**O braço B (agente único com tool calling) não pode funcionar através dessa função como ela está.**

**Lacuna 2 — nenhuma medição de latência existe.**
Busca por `perf_counter`, `time()`, `latency`, `elapsed` em `eval/*.py` e `shared/**/*.py` retorna zero ocorrências.
As métricas secundárias do artigo (p50/p95) não são coletáveis hoje.

**Risco adicional — falha silenciosa contamina a amostra.**
O `except Exception` devolve uma string de desculpa com `tokens_in=0, tokens_out=0` e sem sinalizar falha ao chamador de forma estruturada.
Uma chamada que falhou entra no dataset como se fosse uma resposta. Isso precisa virar falha explícita e contabilizada, não um texto plausível.

*(Observação de escopo: estes são achados do ticket 03; registrados aqui porque afetam diretamente a viabilidade das métricas.)*

### 10.2 Fontes de dados disponíveis, por runtime

**Ollama — `/api/chat` e `/api/generate` retornam contadores e tempos nativos:**
`total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`, `eval_count`, `eval_duration`.
Fonte: <https://github.com/ollama/ollama/blob/main/docs/api.md>
As durações são em **nanossegundos** — converta antes de agregar.

**llama.cpp — objeto `timings` na resposta**, documentado com exemplo:

```js
"timings": {
  "cache_n": 236,               // tokens de prompt reaproveitados do cache
  "prompt_n": 1,                // tokens de prompt processados
  "prompt_ms": 30.958,
  "prompt_per_token_ms": 30.958,
  "prompt_per_second": 32.30,
  "predicted_n": 35,            // tokens gerados
  "predicted_ms": 661.064,
  "predicted_per_token_ms": 18.88,
  "predicted_per_second": 52.94
}
```
Fonte: <https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md>

Há ainda a opção `timings_per_token` para incluir velocidade a cada token, e `--perf/--no-perf` para as métricas internas da libllama.

O campo **`cache_n` é metodologicamente importante**: ele revela reaproveitamento de prefixo de prompt entre requisições.
Num experimento multi-agente, o prompt do supervisor é um prefixo estável e será cacheado — o que **beneficia artificialmente** o braço multi-agente na métrica de latência de prefill.
Registre `cache_n` e discuta-o nas ameaças à validade, ou desabilite o cache de prompt para igualar as condições.

**Caminho OpenAI-compatível — objeto `usage`:** `prompt_tokens`, `completion_tokens`, `total_tokens`.
Em streaming é preciso pedir explicitamente com `stream_options: {"include_usage": true}`.

### 10.3 Padrão de coleta recomendado

O ponto de instrumentação certo é o wrapper que já existe (`llm_completion`), porque ele é o único caminho de chamada — instrumentar ali cobre os dois braços com o mesmo código, o que é exatamente o que um experimento controlado exige.

O que registrar por chamada, em JSONL:

| Campo | Origem |
|---|---|
| `case_id`, `arm`, `repetition`, `node` | do harness |
| `tokens_in` / `tokens_out` | `response.usage.prompt_tokens` / `.completion_tokens` |
| `latency_ms` | `time.perf_counter()` em volta do `await` — mede o que o usuário sente |
| `prompt_ms` / `predicted_ms` / `cache_n` | `timings` do llama.cpp (ou `*_duration` do Ollama) |
| `tool_calls` | `response.choices[0].message.tool_calls` |
| `finish_reason` | `response.choices[0].finish_reason` |
| `ok` / `error` | falha explícita, nunca texto de desculpa |
| `model`, `seed`, `runtime_build` | procedência para reprodutibilidade |

Notas de implementação:
- `perf_counter()` é monotônico e imune a ajuste de relógio; `time.time()` não é.
- **Agregue por caso, não por chamada.** O braço multi-agente faz N chamadas por caso (roteador + especialista + guardrails). Comparar latência *por chamada* entre os braços mede a coisa errada — a métrica do artigo é latência ponta a ponta **por caso**.
- Some tokens do mesmo jeito: o custo do multi-agente é a soma de todas as chamadas do caso.
- p50/p95 exigem amostra suficiente. Com 15 casos, p95 é essencialmente o máximo — considere repetições e declare o método de cálculo do percentil.

### 10.4 O que o LiteLLM oferece (e uma armadilha)

**Uso de tokens:** `response.usage` → `prompt_tokens`, `completion_tokens`, `total_tokens` (classe `Usage` em `litellm/types/utils.py`).
Doc: <https://docs.litellm.ai/docs/completion/token_usage>, que também documenta os helpers `token_counter()`, `completion_cost()` e `cost_per_token()`.

**Armadilha — `response._hidden_params["response_ms"]` não existe.**
Verificado contra `litellm/types/utils.py` e `litellm_core_utils/litellm_logging.py` no `main`: **não encontrado**.
O que existe é `Logging.get_response_ms()`, que calcula `(end_time - start_time).total_seconds() * 1000`, e um kwarg de construtor `response_ms=` em `ModelResponse`.
**Não cite `_hidden_params["response_ms"]` no artigo nem escreva código em cima disso.**

**Caminho documentado para latência — use este:** `CustomLogger`.
Doc: <https://docs.litellm.ai/docs/observability/custom_callback>

```python
from litellm.integrations.custom_logger import CustomLogger
import litellm

class ExperimentLogger(CustomLogger):
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        # kwargs traz "model", "messages", "cache_hit", "response_cost"
        ...

litellm.callbacks = [ExperimentLogger()]
```

**`StandardLoggingPayload`** é o registro estruturado que serve direto para p50/p95 (<https://docs.litellm.ai/docs/proxy/logging_spec>):
`startTime`, `endTime`, `completionStartTime` (*"Time to first token for streaming requests"*), `response_time` (*"Total response time. If streaming, this is the time to first token"*), mais `prompt_tokens`, `completion_tokens`, `total_tokens`, `response_cost`.

**Declarar capacidades de um modelo local** (necessário para o LiteLLM não cair no modo JSON em vez de tool calling nativo):

```python
litellm.register_model(model_cost={
    "ollama_chat/qwen3.5:9b": {"supports_function_calling": True},
})
```
Fonte: <https://docs.litellm.ai/docs/providers/ollama>

### 10.5 Custo

O LiteLLM calcula custo por token a partir de uma tabela de preços de provedores; modelos locais não têm preço nela.
**Para o artigo, "custo" de um modelo local não é dinheiro por token** — é tempo de GPU e energia.
Sugestão: reporte tokens (que é a grandeza medida e auditável) e, se quiser um valor monetário, derive-o de forma declarada (ex.: preço de uma instância equivalente em nuvem × tempo medido), deixando a fórmula explícita no artigo.
Apresentar custo local como se fosse tarifa de API seria um número inventado.

---

## 11. Recomendação final

### Principal — **Qwen3.5-9B**

- **Artefato:** `unsloth/Qwen3.5-9B-GGUF`, arquivo `Qwen3.5-9B-Q6_K.gguf` (7,46 GB) ou `Qwen3.5-9B-Q8_0.gguf` (9,53 GB).
  Alternativa de menor atrito: tag `qwen3.5:9b` do Ollama (6,6 GB), já configurada no `.env.example`.
- **Por quê:**
  1. **Robustez a formato de prompt** — o argumento mais forte, e o menos óbvio. A família Qwen tem o menor `Max Delta` do BFCL V4 (14-18) contra 34-81 de todo o resto (§8.5). Como as duas arquiteturas comparadas neste experimento **necessariamente** formatam o prompt de forma diferente, um modelo frágil a formato afogaria o efeito do tratamento em ruído de harness. Isso vale mais do que alguns pontos de BFCL bruto.
  2. Melhores números públicos de tool calling da faixa: BFCL-V4 **66,1**, TAU2-Bench **79,1** — acima de modelos várias vezes maiores na mesma tabela.
  3. Cabe inteiro na placa **até em Q8_0** (9,12 GiB com KV a 8K). Permite rodar **Q4_K_M como ponto de operação e Q8_0 como controle**, transformando a escolha de quantização de suposição em resultado (§4.1) — argumento metodológico que nenhum 27B permite nesta placa.
  4. KV cache minúsculo (0,25 GiB a 8K; ~1,07 GB a 32K) por causa da arquitetura híbrida Gated DeltaNet. Num experimento multi-agente, onde a transcrição acumula chamadas e resultados de ferramenta ao longo dos agentes, **o KV é o termo dominante de VRAM, não os pesos** — um 14B convencional gastaria 5,37 GiB no mesmo contexto de 32K.
  5. Badge `tools` na biblioteca do Ollama, template verificado (`tools`, `tool_call`, `<tool_response>` presentes no `tokenizer_config.json`), e comandos de tool calling documentados no model card para vLLM e SGLang.
  6. É o modelo que o repositório já usa — zero mudança de baseline, e o histórico de desenvolvimento do projeto continua válido.
  7. 201 idiomas declarados; o eval set é em português (`eval/eval_set.jsonl`, 15 casos, `"language": "pt"`).
- **Custos a assumir, declarados:**
  - Não existe GGUF de primeira parte (a Qwen não publica GGUF para 3.5/3.6). O `unsloth/Qwen3.5-9B-GGUF` é comunitário — valide o template de chat depois de baixar.
  - **Thinking vem ligado por padrão.** Desligue com `chat_template_kwargs: {"enable_thinking": false}`, ou o tempo de "pensamento" domina a latência medida e vira um confundidor entre braços.
  - O 66,1 é auto-reportado contra um quadro congelado em abril/2026 (§8.4). Calibração parcial: a Qwen pontua o Qwen3-30B-A3B-Thinking-2507 em 42,4 e o CSV oficial tem o Qwen3-30B-A3B-**Instruct**-2507 (FC) em 41,39 — variantes diferentes, ~1 ponto de distância, o que sugere que o harness deles não é absurdamente inflado. Trate como crível-porém-não-replicado.
  - A tag `qwen3.5:9b` do Ollama tem 6,6 GB porque empacota o projetor de visão junto (5,68 GB de GGUF + 0,92 GB de `mmproj`). Para um experimento só de texto, isso é ~0,9 GB de VRAM desperdiçado.

### Reserva — **Gemma 4 12B Unified**

- **Artefato preferido — GGUF QAT de primeira parte do Google:** <https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf> → `gemma-4-12b-it-qat-q4_0.gguf`, **6,98 GB**, Apache 2.0.
  QAT (quantization-aware training) é qualitativamente diferente de quantização pós-treino: o modelo foi treinado sabendo que seria quantizado. Além disso, ser artefato de primeira parte remove a dúvida de procedência que o GGUF comunitário do Qwen carrega.
  Alternativas: `unsloth/gemma-4-12b-it-GGUF` `Q5_K_M` (8,41 GB), ou as tags `gemma4:12b` (7,6 GB) / `gemma4:12b-it-qat` (7,2 GB) do Ollama.
- **Por quê:**
  1. τ²-Bench **69,0%** reportado pelo Google, com function calling nativo declarado.
  2. Cabe com folga (8,64 GiB a 8K com Q5_K_M; menos ainda com o QAT q4_0).
  3. **Fabricante e arquitetura diferentes do principal** — é o que torna uma reserva útil. Se o resultado depender de idiossincrasias do Qwen, trocar por um Gemma revela isso.
  4. O llama.cpp tem parser de tool call **dedicado** ao Gemma 4 (`COMMON_CHAT_FORMAT_PEG_GEMMA4`), e o vLLM tem `--tool-call-parser gemma4`. Template nativo confirmado por leitura do `chat_template.jinja`: recebe `tools`, emite `<|tool_call|>call:<nome>{…}<tool_call|>` e `<|tool_response|>`.
  5. Excelente perfil de KV por causa da janela deslizante (8 camadas globais + 40 deslizantes de 1024): 0,81 GiB a 8K, ~2,48 GB a 32K.
  6. É o *mesmo modelo* do candidato 2 original do autor — na embalagem certa para esta placa. **O instinto do autor sobre o modelo estava correto; só o formato do artefato estava errado.**
- **Custo declarado:** o card do Gemma 4 **não publica nenhum benchmark específico de function calling** além do Tau2 — não há BFCL, ACEBench nem Nexus. A frase *"Native support for structured tool use"* é afirmação, não medição. Nota histórica útil: a limitação clássica "Gemma não tem template de ferramentas" acabou no Gemma 4 — o `gemma3` no Ollama não tem badge `tools`, o `gemma4` tem.

### Alternativa de reserva, se for desejável contraste arquitetural máximo

**`ibm-granite/granite-4.1-8b`** (Ollama `granite4.1:8b`, 5,3 GB) — **BFCL v3 68,27** publicado em tabela de avaliação de primeira parte, Apache 2.0, parser dedicado no vLLM, e uma escada 3B/8B/30B se o autor quiser um segundo eixo de escala.
É a opção com a evidência de tool calling mais bem documentada *pelo próprio fabricante* da lista.
Custo: atenção full em todas as 40 camadas → KV de 5,37 GiB a 32K, o que limita o contexto a 8K-16K nesta placa.

### Curinga metodológico, se sobrar tempo

**`qwen3.5:4b` em BF16 (9,3 GB)** — BFCL-V4 50,3, TAU2-Bench 79,9.
É a **única** opção que cabe totalmente **sem quantização** em 12 GB.
Dado que ninguém publicou BFCL por nível de quant GGUF (§4.1), um braço com quantização eliminada por completo é um controle que vale mais para a validade do artigo do que a diferença bruta de capacidade contra o 9B.

### Runtime

Duas opções válidas, com um trade-off real:

- **Ollama** — menor atrito: já está cabeado, roda nativo em Windows, tem `tools`, `seed`, `format` (JSON schema) e contadores de token/tempo na resposta.
  Exige uma correção: trocar o prefixo do LiteLLM de `ollama/` para `ollama_chat/` (§7.4), senão o braço B não recebe `tools`.
  **Limitação dura: não suporta `tool_choice`** (§7.2) — não dá para forçar uma chamada de ferramenta.
- **`llama-server`** (binários Windows CUDA oficiais em <https://github.com/ggml-org/llama.cpp/releases>) — mais rigor: `seed` por requisição, objeto `timings` detalhado com `cache_n`, `cache_prompt: false` para reprodutibilidade, tool calls restritos por gramática, `tool_choice` (verificado no código, §7.1) e `-ngl` explícito.
  Custo: um servidor a mais para configurar, e o LiteLLM passa a apontar para ele como endpoint OpenAI-compatível (`openai/` + `api_base`, já que não existe provider `llamacpp` — §7.4).

**Sugestão:** desenvolva com Ollama, e faça as **execuções medidas** com `llama-server`.

O que inclina a balança não é conveniência, são três coisas que só o llama-server entrega e que o artigo precisa:
1. `cache_prompt: false` — remove a fonte de não-determinismo documentada **e** a vantagem artificial de cache de prefixo do braço multi-agente, de uma vez (§9.2, §10.2).
2. `cache_n` no `timings` — torna o efeito de cache de prompt **mensurável** em vez de invisível.
3. `tool_choice` e gramática — separam falha de sintaxe de falha de semântica, que é a distinção que o paper de quantização mostra ser essencial (§4.1).

Se o cronograma não permitir, Ollama com seed fixa, `num_gpu` explícito e amostragem sobrescrita é defensável — desde que as três limitações acima sejam declaradas nas ameaças à validade.

**vLLM está fora** (não roda nativo em Windows), apesar de ser o único com página oficial de reprodutibilidade e interruptor de invariância de batch (§9.3). Vale registrar como caminho de replicação em Linux.

### Não recomendados, com o motivo em uma linha

- `unsloth/gemma-4-12b-it-NVFP4` — formato sem aceleração nativa em Ampere, runtime sem suporte a Windows, e sem caminho de conversão para GGUF.
- `prism-ml/Bonsai-27B-gguf` — a compressão de 1 bit custa 21,6 pontos em τ²-Bench, exatamente a capacidade sob teste (opcionalmente útil como terceiro braço de sensibilidade, §3.7).
- Qualquer 27B convencional em Q4 — 17 GB não cabem em 12 GB, e rodar com offload mede a banda da DDR, não a arquitetura do agente.

---

## 12. Achados sobre o repositório que afetam este ticket

Levantados durante a pesquisa, todos verificáveis no código. Nenhum arquivo foi modificado.

1. **O braço multi-agente atual não usa tool calling do LLM.**
   `services/agent_api/application/tools.py` mapeia intenção → ferramentas por um dicionário fixo (`INTENT_TOOLS`) e executa via `execute_tools_for_intent()`.
   Não há `bind_tools` nem leitura de `tool_calls` em `services/agent_api/application/agent.py`.
   **Consequência para o desenho experimental:** o braço A nunca corre o risco de emitir uma chamada de ferramenta malformada; o braço B corre.
   A comparação, como está, mistura "arquitetura multi-agente" com "roteamento determinístico vs roteamento pelo modelo".
   Isso precisa ser resolvido no protocolo (ticket 05) — ou controlado, ou declarado como parte do tratamento.
   É também o motivo pelo qual a confiabilidade de tool calling do modelo escolhido importa tanto: ela penaliza um braço só.

2. **Prefixo do LiteLLM roteia para o endpoint errado** — `ollama/` → `/api/generate`; precisa ser `ollama_chat/` → `/api/chat` para `tools` funcionar (§7.4).

3. **`llm_completion()` descarta `tool_calls`** (§10.1).

4. **Não há instrumentação de latência** em `eval/runner.py` nem em `shared/` (§10.1).

5. **Falha de LLM retorna texto de desculpa com tokens zerados**, sem sinalizar erro estruturado — contamina a amostra (§10.1).

6. **`eval/eval_set.jsonl` tem 15 casos**, com `expected_tool` já definido por caso — boa base para um oráculo de sucesso de tarefa, mas 15 casos são pouco para p95 sem repetições.

7. **As 10 ferramentas têm assinaturas simples e planas** (`customer_id`, `card_id`, `limit`, `cep`), sem objetos aninhados.
   **[INFERÊNCIA]** Isso coloca a dificuldade de tool calling na faixa baixa-média, o que reforça a suficiência de um modelo 9B-12B: o gargalo do experimento será escolha de ferramenta e roteamento, não formatação de argumentos complexos.

---

## 13. Lacunas — o que não foi encontrado

Registrado explicitamente para não virar estimativa disfarçada de fato.

- Valor oficial da reserva de VRAM do Windows/WDDM para display — **medir com `nvidia-smi`**.
- Número de throughput NVFP4 vs baseline medido em Ampere.
- Benchmark primário varrendo `-ngl` num modelo **denso** em RTX 3060 (o que existe é de modelo MoE, e não transfere).
- Medição do Bonsai-27B especificamente numa RTX 3060 (existe para 3080 Ti, 3080, A2000, L40S).
- **Medição de BFCL/τ²-bench por nível de quantização GGUF, mesmo modelo** — nenhum paper, model card ou doc da Unsloth publica. Esta é a lacuna que o próprio experimento pode fechar (§4.1).
- Estudo cruzando nível de quantização × decodificação restrita, separando correção sintática de semântica (§7.6).
- Declaração oficial de garantia de determinismo bit-a-bit do Ollama (a doc diz "reproducible outputs", sem ressalva de hardware/batching).
- `tool_choice: required` no llama.cpp está no código-fonte mas **não na documentação** — validar empiricamente na build usada.
- Entradas de Qwen3.5, Granite 4.1 e Gemma 4 no quadro **oficial** do BFCL — os CSVs estão congelados em 13/abr/2026, então os números desses modelos são todos auto-reportados.
- Valores aceitos de `CUBLAS_WORKSPACE_CONFIG` — ausentes da nota de aleatoriedade do PyTorch consultada; não citar sem reverificar.

---

## 14. Checklist de verificação antes de gravar medições

**VRAM e offload**
1. `nvidia-smi --query-gpu=memory.total,memory.free --format=csv` com a área de trabalho ociosa → estabelece o teto real e a reserva do Windows que não está documentada.
2. Fixar `-ngl` / `num_gpu` **explicitamente** no número total de camadas (32 para Qwen3.5-9B, 48 para Gemma 4 12B). Nunca deixar em `auto`.
3. Ler o log de inicialização e confirmar que **todas** as camadas foram para `CUDA0`; anotar `compute buffer size` e `output buffer size`.
4. Reexecutar `nvidia-smi` sob carga: se a VRAM usada estiver abaixo do teto e o tok/s for estável entre execuções, a métrica está limpa.

**Amostragem e reprodutibilidade**
5. Fixar `seed` e `temperature=0`, **e sobrescrever `top_k`, `top_p` e `min_p`** — os defaults do llama.cpp não são neutros (§9.2).
6. Enviar `"cache_prompt": false` nas execuções medidas (llama.cpp).
7. Desligar o modo thinking (`enable_thinking: false` no Qwen3.5), ou o tempo de raciocínio domina a latência e vira confundidor entre braços.
8. Fixar `num_ctx` / `-c` em 8192 nos dois braços — contexto diferente muda alocação de KV e latência.
9. Manter o KV em `f16` nos dois braços; nunca variar quantização de peso e de KV no mesmo experimento (§5.5).
10. Registrar build do runtime, digest da tag do modelo, seed e temperatura em **cada linha** do JSONL.
11. Rodar uma sequência por vez, sem concorrência, durante as medições.
12. Rodar N repetições por célula e **reportar a variação observada** — é a única forma honesta de tratar determinismo em GPU.

**Instrumentação e métricas**
13. Registrar `cache_n` (llama.cpp) e discutir o efeito de cache de prefixo nas ameaças à validade.
14. **Separar `valid_json@1`, `correct_function@1` e `correct_args@1` do sucesso de tarefa** — um número agregado com orçamento de retry comprovadamente esconde amplificação de erro de 2,5× (§4.1).
15. Agregar latência e tokens **por caso**, não por chamada — o braço multi-agente faz N chamadas por caso.
16. Falha de LLM vira erro explícito e contabilizado, nunca texto de desculpa com tokens zerados (§10.1).

**Antes de culpar o modelo**
17. Se a taxa de invocação de ferramenta der perto de 0%, cheque se `tools` e schema de resposta estruturada estão ligados ao mesmo tempo (§7.5) antes de atribuir ao modelo ou à quantização.
