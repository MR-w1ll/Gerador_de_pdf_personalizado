from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt 
from io import BytesIO
import numpy as np
import math


PATH_BASE_FONTES = 'fontes'

PATH_PAGINAS = {
    1:'templates_paginas/1.png',
    2:'templates_paginas/2.png',
    3:'templates_paginas/3.png',
    4:'templates_paginas/4.png',
    5:'templates_paginas/5.png',
    6:'templates_paginas/6.png',
    7:'templates_paginas/7.png',
    8:'templates_paginas/8.png',
    9:'templates_paginas/9.png',
    10:'templates_paginas/10.png',
}

PATH_FONTES = {
    'Sugo_Pro_Display':{
        'ExtraLight-trial':f'{PATH_BASE_FONTES}/sugo_pro_display/Sugo-Pro-Display-ExtraLight-trial.ttf'
    },

    'Arial':{
        'Arial-Normal':'arial.ttf'    
    },

    'akzidenz-grotesk':{
        'akzidenz-grotesk':f'{PATH_BASE_FONTES}/akzidenz-grotesk/akzidenz-grotesk.ttf',
        'akzidenz-grotesk-bold':f'{PATH_BASE_FONTES}/akzidenz-grotesk/akzidenz-grotesk-bold.ttf'
    },
}


class GERADOR_DE_APRESENTACAO():

    def __init__(self, configuracoes):
        self.paginas_personalizadas = {}

        for confg in configuracoes:

            num_pagina = confg['pagina']
            curvado         = confg['curvado']
            grafico         = confg['grafico']

            if not num_pagina in self.paginas_personalizadas.keys():
                self.paginas_personalizadas[num_pagina] = None

            if curvado:
                raio            = confg['raio']
                centro          = confg['centro']
                angulo_inicial  = confg['angulo_inicial']
                espacamento     = confg['espacamento']
                orientacao      = confg['orientacao']
                alinhamento     = confg['alinhamento']

                self.adicionar_texto_curvado(num_pagina, texto, cor, fonte, raio, centro, angulo_inicial, espacamento, orientacao, alinhamento)

            elif grafico:
                tipo   = confg['grafico_tipo']
                pos_xy = confg['pos_xy']
                tamanho_do_grafico = confg['tamanho_do_grafico']

                if tipo == 'linha':
                    dados_do_grafico   = confg['dados_do_grafico']

                    self.inserir_grafico_linha(num_pagina, pos_xy, tamanho_do_grafico, None, dados_do_grafico)

                elif tipo == 'linha_funcao':
                    self.inserir_grafico_linha_funcao()

                elif tipo == 'pizza':
                    dados_do_grafico   = confg['dados_do_grafico']

                    self.inserir_grafico_pizzas(num_pagina, pos_xy, tamanho_do_grafico, None, dados_do_grafico, None)

                elif tipo == 'barra':
                    dados_1 = confg['dados_1']
                    dados_2 = confg['dados_2']
                    
                    self.inserir_grafico_barras(num_pagina, pos_xy, tamanho_do_grafico, None, dados_1, dados_2, None, None)

                elif tipo == 'barra_deitada':
                    dados_do_grafico = confg['dados_do_grafico']

                    self.inserir_grafico_barras_deitadas(num_pagina, pos_xy, tamanho_do_grafico, None, dados_do_grafico, None)
                    
                else:
                    
                    dados_milhas  = confg['dados_do_grafico']
                    tamanho       = confg['tamanho_do_grafico']
                    self.inserir_grafico_milhas(num_pagina, dados_milhas, pos_xy, tamanho)
            
            else:
                texto      = confg['texto']
                pos_xy     = confg['pos_xy']
                cor        = confg['cor']
                fonte      = confg['fonte']
                alinhamento            = confg['alinhamento_texto']
                tamanho_caixa_de_texto = confg['tamanho_caixa_de_texto']
                margem                 = confg['margem_texto']
                espacamento            = confg['espacamento_texto']

                self.adicionar_texto(num_pagina, texto, pos_xy, cor, fonte, alinhamento, tamanho_caixa_de_texto, margem, espacamento)


        self.pdf = self.fazer_pdf(self.paginas_personalizadas)
        
        


    def adicionar_texto(self, pagina, texto, pos_xy, cor, fonte,
                        alinhamento, tamanho_caixa_de_texto, margem, espacamento):
        
        if self.paginas_personalizadas[pagina] != None:
            imagem = self.paginas_personalizadas[pagina]
        else:
            # Caminho para a imagem PNG de base
            caminho_imagem = PATH_PAGINAS[pagina]
            # Abrir a imagem
            imagem = Image.open(caminho_imagem).convert("RGBA")


        

        img_texto = self.escrever_texto_na_imagem(texto, alinhamento, tamanho_caixa_de_texto, fonte['caminho'], cor, fonte['tamanho'], margem, espacamento)
        
        pos_x, pos_y = pos_xy
        # Cola o gráfico na imagem base
        imagem.paste(img_texto, (int(pos_x), int(pos_y)), img_texto)

        self.paginas_personalizadas[pagina] = imagem

        print("Texto inserido com sucesso.")

    def adicionar_texto_curvado(self, pagina, texto, cor, fonte, raio, centro, angulo_inicial, espacamento, orientacao, alinhamento):
        # ========= CONFIGURAÇÕES =========
        TEXTO = texto
        RAIO = raio
        CENTRO = centro
        ANGULO_INICIAL = angulo_inicial  # graus
        ESPACAMENTO = espacamento       # pixels extras entre letras
        ORIENTACAO = orientacao   # "fora" ou "dentro"
        ALINHAMENTO = alinhamento  # "cima" ou "baixo"
        # =================================

        caminho_fonte = fonte['caminho']  # Altere conforme sua fonte
        tamanho_fonte = fonte['tamanho']

        # Preparar fonte
        fonte = ImageFont.truetype(caminho_fonte, tamanho_fonte)

        if self.paginas_personalizadas[pagina] != None:
            img = self.paginas_personalizadas[pagina]
        else:
            # Caminho para a imagem PNG de base
            caminho_imagem = PATH_PAGINAS[pagina]
            # Abrir a imagem
            img = Image.open(caminho_imagem).convert("RGBA")


        draw = ImageDraw.Draw(img)

        # Medir largura total do texto com espaçamento extra
        largura_total = sum(fonte.getlength(c) + ESPACAMENTO for c in TEXTO)
        angulo_por_pixel = 180 / (math.pi * RAIO)

        # Ângulo atual ajustado ao centro do arco
        angulo = ANGULO_INICIAL - (largura_total / 2) * angulo_por_pixel

        for caractere in TEXTO:
            largura = fonte.getlength(caractere) + ESPACAMENTO
            angulo_central = angulo + (largura / 2) * angulo_por_pixel
            angulo_rad = math.radians(angulo_central)

            # Posição da letra
            x = CENTRO[0] + RAIO * math.cos(angulo_rad)
            y = CENTRO[1] + RAIO * math.sin(angulo_rad)

            # Criar imagem da letra
            letra_img = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
            letra_draw = ImageDraw.Draw(letra_img)
            letra_draw.text((50, 50), caractere, font=fonte, fill=cor, anchor="mm")

            # Determinar rotação da letra para acompanhar a curva e orientação
            if ORIENTACAO == "fora":
                rotacao = -angulo_central + 90
            else:  # "dentro"
                rotacao = -angulo_central - 90

            # Corrigir rotação se o texto está na parte de baixo
            if ALINHAMENTO == "baixo":
                rotacao += 180

            rotacionada = letra_img.rotate(rotacao, center=(50, 50), resample=Image.BICUBIC)

            # Compor imagem
            img.alpha_composite(rotacionada, (int(x) - 50, int(y) - 50))

            # Avançar
            angulo += largura * angulo_por_pixel

        # Salvar imagem
        self.paginas_personalizadas[pagina] = img
        # self.paginas_personalizadas.append(img)
        # img.save("texto_curvado_orientado.png")

        print("Texto curvado com controle de orientação gerado com sucesso.")

    def escrever_texto_na_imagem(
        self,
        texto,
        alinhamento,
        tamanho_imagem,
        caminho_fonte,
        cor_texto,
        tamanho_fonte,
        margem = 20,
        espacamento = 5
    ):
        # Imagem RGBA com fundo transparente
        imagem = Image.new('RGBA', tamanho_imagem, color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(imagem)

        fonte = ImageFont.truetype(caminho_fonte, tamanho_fonte)

        largura_maxima = tamanho_imagem[0] - 2 * margem
        palavras = texto.split()
        linhas = []
        linha = ""

        # Quebra de linha
        for palavra in palavras:
            teste_linha = linha + palavra + " "
            bbox = draw.textbbox((0, 0), teste_linha, font=fonte)
            largura_teste = bbox[2] - bbox[0]
            if largura_teste <= largura_maxima:
                linha = teste_linha
            else:
                linhas.append(linha.strip())
                linha = palavra + " "
        linhas.append(linha.strip())

        # Escrever texto com alinhamento
        y = margem
        for i, linha in enumerate(linhas):
            bbox = draw.textbbox((0, 0), linha, font=fonte)
            largura_linha = bbox[2] - bbox[0]

            if alinhamento.lower() == "esquerda":
                x = margem
            elif alinhamento.lower() == "direita":
                x = tamanho_imagem[0] - margem - largura_linha
            elif alinhamento.lower() == "centralizado":
                x = (tamanho_imagem[0] - largura_linha) // 2
            elif alinhamento.lower() == "justificado" and i != len(linhas) - 1:
                palavras_linha = linha.split()
                if len(palavras_linha) == 1:
                    x = margem
                else:
                    largura_total = sum(
                        draw.textbbox((0, 0), p, font=fonte)[2] - draw.textbbox((0, 0), p, font=fonte)[0]
                        for p in palavras_linha
                    )
                    espaco_total = largura_maxima - largura_total
                    espaco_entre = espaco_total // (len(palavras_linha) - 1)
                    x = margem
                    for palavra in palavras_linha:
                        draw.text((x, y), palavra, fill=cor_texto + (255,), font=fonte)
                        largura_palavra = draw.textbbox((0, 0), palavra, font=fonte)[2] - draw.textbbox((0, 0), palavra, font=fonte)[0]
                        x += largura_palavra + espaco_entre
                    y += tamanho_fonte + espacamento
                    continue
            else:
                x = margem  # fallback

            draw.text((x, y), linha, fill=cor_texto + (255,), font=fonte)
            y += tamanho_fonte + espacamento

        return imagem



    # Graficos ------------------------------------------
    def inserir_grafico_milhas(self, pagina, dados_milhas, posicao, tamanho):
        """
        Adiciona um gráfico de milhas por mês à imagem_base.

        Parâmetros:
        - imagem_base (PIL.Image): imagem onde o gráfico será inserido.
        - dados_milhas (dict): Ex: {'Cartão A': [1000, 2000, 3000, ...], 'Cartão B': [500, 700, 900, ...]}
        - posicao (tuple): (x, y) onde o gráfico será colado na imagem.
        - tamanho (tuple): (largura, altura) do gráfico.
        """


        if self.paginas_personalizadas[pagina] != None:
            imagem_base = self.paginas_personalizadas[pagina]
        else:
            # Caminho para a imagem PNG de base
            caminho_imagem = PATH_PAGINAS[pagina]
            # Abrir a imagem
            imagem_base = Image.open(caminho_imagem).convert("RGBA")


        # Meses fixos
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        # Cria o gráfico com matplotlib
        fig, ax = plt.subplots(figsize=(8, 4))
        for nome_cartao, milhas in dados_milhas.items():
            ax.plot(meses[:len(milhas)], milhas, marker='o', label=nome_cartao)

        ax.set_title("Milhas acumuladas por mês")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Milhas")
        ax.legend()
        ax.grid(True)

        # Salva o gráfico em memória
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='PNG', transparent=True)
        plt.close(fig)
        buffer.seek(0)

        # Carrega o gráfico como imagem PIL
        grafico_img = Image.open(buffer)

        # Redimensiona o gráfico para o tamanho desejado
        grafico_redimensionado = grafico_img.resize(tamanho)

        # Cola o gráfico na imagem base
        imagem_base.paste(grafico_redimensionado, posicao, grafico_redimensionado)

        print("Gráfico inserido com sucesso.")
        self.paginas_personalizadas[pagina] = imagem_base
        # return imagem_base


    def inserir_grafico_barras_deitadas(self, pagina, posicao, tamanho,
                                        categorias=None, valores=None, cor_barras=None):
        
        if self.paginas_personalizadas[pagina] is not None:
            imagem_base = self.paginas_personalizadas[pagina]
        else:
            caminho_imagem = PATH_PAGINAS[pagina]
            imagem_base = Image.open(caminho_imagem).convert("RGBA")

        categorias = categorias or [
            'Integração de dados',
            'Conformidade com regulamentações',
            'Controle de custos e prevenção de erros',
            'Adaptação à transformação digital'
        ]
        valores = valores or [12, 15, 18, 40]
        cor_barras = cor_barras or '#6db07b'

        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#f8ecdf')
        barras = ax.barh(categorias, valores, color=cor_barras, edgecolor='none')

        for barra in barras:
            largura = barra.get_width()
            ax.text(largura + 1, barra.get_y() + barra.get_height() / 2,
                    f'{int(largura)}', va='center', ha='left',
                    fontsize=10, weight='bold', color='#333333')

        ax.invert_yaxis()
        ax.set_xlim(0, max(valores) + 10)
        ax.set_facecolor('#f8ecdf')
        ax.tick_params(axis='x', labelsize=10)
        ax.tick_params(axis='y', labelsize=10)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.xaxis.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', transparent=True)
        plt.close(fig)
        buffer.seek(0)
        grafico_img = Image.open(buffer)
        grafico_redimensionado = grafico_img.resize(tamanho)
        imagem_base.paste(grafico_redimensionado, posicao, grafico_redimensionado)

        self.paginas_personalizadas[pagina] = imagem_base


    def inserir_grafico_barras(self, pagina, posicao, tamanho,
                            categorias=None, contabil=None, financeiro=None,
                            cor_contabil=None, cor_financeiro=None):
        
        if self.paginas_personalizadas[pagina] is not None:
            imagem_base = self.paginas_personalizadas[pagina]
        else:
            caminho_imagem = PATH_PAGINAS[pagina]
            imagem_base = Image.open(caminho_imagem).convert("RGBA")

        categorias = categorias or ['Item 1', 'Item 2', 'Item 3', 'Item 4']
        contabil = contabil or [8, 12, 15, 20]
        financeiro = financeiro or [5, 10, 12, 22]
        cor_contabil = cor_contabil or '#0d1f14'
        cor_financeiro = cor_financeiro or '#2d6a2d'
        x = np.arange(len(categorias))

        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#f8ecdf')
        ax.bar(x, contabil, color=cor_contabil, label='Contábil')
        ax.bar(x, financeiro, bottom=contabil, color=cor_financeiro, label='Financeiro')
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, fontsize=10, weight='bold')
        ax.set_title('Desempenho por Área', fontsize=14, weight='bold', pad=15, color='#333333')
        ax.set_ylabel('Valores', fontsize=10, weight='bold')
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, linestyle='--', alpha=0.5)
        ax.set_facecolor('#f8ecdf')
        ax.tick_params(axis='y', labelsize=10)
        ax.legend(loc='upper center', ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 1.1))
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', transparent=True)
        plt.close(fig)
        buffer.seek(0)
        grafico_img = Image.open(buffer)
        grafico_redimensionado = grafico_img.resize(tamanho)
        imagem_base.paste(grafico_redimensionado, posicao, grafico_redimensionado)
        self.paginas_personalizadas[pagina] = imagem_base


    def inserir_grafico_linha_funcao(self, pagina, posicao, tamanho,
                                    aporte_mensal=100, taxa_juros_mensal=0.01, periodo_meses=12,
                                    fundo_cor='#f8ecdf', linha_cor='#2d6a2d',
                                    titulo_grafico='Evolução do Investimento com Juros Compostos',
                                    rotulo_x='Meses', rotulo_y='Valor acumulado (R$)'):

        if self.paginas_personalizadas[pagina] is not None:
            imagem_base = self.paginas_personalizadas[pagina]
        else:
            caminho_imagem = PATH_PAGINAS[pagina]
            imagem_base = Image.open(caminho_imagem).convert("RGBA")

        meses = np.arange(1, periodo_meses + 1)
        valores_acumulados = [
            aporte_mensal * ((1 + taxa_juros_mensal) ** m - 1) / taxa_juros_mensal
            for m in meses
        ]

        fig, ax = plt.subplots(figsize=(10, 5), facecolor=fundo_cor)
        ax.plot(meses, valores_acumulados, color=linha_cor, linewidth=2.5,
                linestyle='-', label='Investimento Acumulado')
        ax.set_title(titulo_grafico, fontsize=14, weight='bold', pad=15)
        ax.set_xlabel(rotulo_x, fontsize=12, weight='bold')
        ax.set_ylabel(rotulo_y, fontsize=12, weight='bold')
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.4)
        ax.set_facecolor(fundo_cor)
        ax.tick_params(axis='both', labelsize=10)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.legend(loc='upper left', frameon=False, fontsize=10)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', transparent=True)
        plt.close(fig)
        buffer.seek(0)
        grafico_img = Image.open(buffer)
        grafico_redimensionado = grafico_img.resize(tamanho)
        imagem_base.paste(grafico_redimensionado, posicao, grafico_redimensionado)
        self.paginas_personalizadas[pagina] = imagem_base


    def inserir_grafico_linha(self, pagina, posicao, tamanho,
                            categorias=None, valores=None):
        if self.paginas_personalizadas[pagina] is not None:
            imagem_base = self.paginas_personalizadas[pagina]
        else:
            caminho_imagem = PATH_PAGINAS[pagina]
            imagem_base = Image.open(caminho_imagem).convert("RGBA")

        categorias = categorias or ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
        valores = valores or [22, 28, 30, 40, 48]

        fig, ax = plt.subplots(figsize=(6, 2.5), facecolor='#f8ecdf')
        ax.plot(categorias, valores, color='#1b4024', marker='o',
                linestyle='-', linewidth=1.5, markersize=4)
        ax.set_facecolor('#f8ecdf')
        ax.tick_params(axis='x', labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        ax.yaxis.grid(True, linestyle='--', linewidth=0.6, alpha=0.4)
        ax.xaxis.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', transparent=True)
        plt.close(fig)
        buffer.seek(0)
        grafico_img = Image.open(buffer)
        grafico_redimensionado = grafico_img.resize(tamanho)
        imagem_base.paste(grafico_redimensionado, posicao, grafico_redimensionado)
        self.paginas_personalizadas[pagina] = imagem_base


    def inserir_grafico_pizzas(self, pagina, posicao, tamanho,
                                labels=None, dados=None, cores=None):
        if self.paginas_personalizadas[pagina] is not None:
            imagem_base = self.paginas_personalizadas[pagina]
        else:
            caminho_imagem = PATH_PAGINAS[pagina]
            imagem_base = Image.open(caminho_imagem).convert("RGBA")

        labels = labels or ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
        dados = dados or [20, 20, 20, 20, 20]
        cores = cores or ['#0d1f14', '#6db07b', '#2d6a2d', '#5e6b5e', '#39633d']

        fig, ax = plt.subplots(figsize=(6, 6), facecolor='#f8ecdf')
        wedges, texts, autotexts = ax.pie(dados, labels=labels, colors=cores,
            startangle=90, counterclock=False,
            wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
            autopct='%1.0f%%', pctdistance=0.85,
            textprops={'fontsize': 10, 'weight': 'bold'})

        for text in texts:
            text.set_fontsize(10)
            text.set_weight('bold')
            text.set_color('black')
        ax.axis('equal')
        plt.title('Distribuição dos Itens', fontsize=14, weight='bold', color='#333333', pad=20)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', transparent=True)
        plt.close(fig)
        buffer.seek(0)
        grafico_img = Image.open(buffer)
        grafico_redimensionado = grafico_img.resize(tamanho)
        imagem_base.paste(grafico_redimensionado, posicao, grafico_redimensionado)
        self.paginas_personalizadas[pagina] = imagem_base



    def fazer_pdf(self, lista_imagens):
            """
            Recebe uma lista de objetos PIL.Image e retorna um PDF em memória (BytesIO).
            """
            lista_ordenada = dict(sorted(lista_imagens.items()))
            
            # Converter todas as imagens para RGB
            imagens_rgb = [img.convert("RGB") for img in lista_ordenada.values()]

            # PDF em memória
            pdf_em_memoria = BytesIO()
            imagens_rgb[0].save(pdf_em_memoria, format="PDF", save_all=True, append_images=imagens_rgb[1:])
            pdf_em_memoria.seek(0)

            # Agora salve isso em um arquivo PDF no disco
            with open("saida_final.pdf", "wb") as f:
                f.write(pdf_em_memoria.getbuffer())

            # response = HttpResponse(pdf_em_memoria.getvalue(), content_type='application/pdf')
            # response['Content-Disposition'] = f'attachment; filename="cotacao_{1}.pdf"'
            return pdf_em_memoria

    def coletar_pdf(self):
        return self.pdf




confg = [
    {
    'pagina':1,
    'texto':'Gestão Financeira e Contábil'.upper(),
    'pos_xy':(176, 279),
    'cor':(247, 237, 225),
    'alinhamento_texto':'esquerda',
    'tamanho_caixa_de_texto': (950, 398),
    'margem_texto': 25,
    'espacamento_texto': 5,

    'fonte':{
        'caminho':PATH_FONTES['akzidenz-grotesk']['akzidenz-grotesk-bold'], 
        'tamanho':125,
    },

    'curvado':False,
    'grafico':False,
    },

    {
    'pagina':2,
    'texto':'A integração entre os setores financeiro e contábil é essencial para garantir uma gestão eficiente e segura. Enquanto o financeiro lida com o controle de caixa, entradas, saídas e projeções, a contabilidade registra, organiza e interpreta esses dados sob a ótica legal e patrimonial. Quando atuam de forma desconectada, surgem falhas nos relatórios, erros de apuração e riscos no cumprimento de obrigações fiscais.',

    'pos_xy':(272, 414),
    'cor':(0, 0, 0),
    'alinhamento_texto':'centralizado',
    'tamanho_caixa_de_texto': (670, 700),
    'margem_texto': 20,
    'espacamento_texto':5,

    'fonte':{
        'caminho':PATH_FONTES['akzidenz-grotesk']['akzidenz-grotesk'], 
        'tamanho':25,
    },

    'curvado':False,
    'grafico':False,
    },

    {
    'pagina':2,
    'texto':'A integração entre os setores financeiro e contábil é uma das melhores práticas para alcançar eficiência, segurança e inteligência na gestão corporativa. O setor financeiro projeta, controla e executa o fluxo de recursos, enquanto a contabilidade registra e analisa esses dados conforme as normas legais. Quando atuam de forma alinhada, reduzem-se erros, retrabalhos e riscos fiscais, além de garantir relatórios mais precisos e confiáveis.',

    'pos_xy':(1125, 414),
    'cor':(0, 0, 0),
    'alinhamento_texto':'centralizado',
    'tamanho_caixa_de_texto': (670, 700),
    'margem_texto': 20,
    'espacamento_texto':5,

    'fonte':{
        'caminho':PATH_FONTES['akzidenz-grotesk']['akzidenz-grotesk'], 
        'tamanho':25,
    },

    'curvado':False,
    'grafico':False,
    },


    {
    'pagina':3,
    'pos_xy':(1181, 289),
    'curvado':False,
    'grafico':True,
    'grafico_tipo':'pizza',
    'dados_do_grafico': [30, 10, 15, 25, 20],
    'tamanho_do_grafico':(632, 578),
    },

    {
    'pagina':4,
    'pos_xy':(1081, 472),
    'curvado':False,
    'grafico':True,
    'grafico_tipo':'barra',
    'dados_1': [12, 20, 32, 51],
    'dados_2': [7, 11, 18, 26],
    'tamanho_do_grafico':(666, 501),
    },

    {
    'pagina':5,
    'pos_xy':(143, 312),
    'curvado':False,
    'grafico':True,
    'grafico_tipo':'barra_deitada',
    'dados_do_grafico': [12, 20, 25, 51],
    'tamanho_do_grafico':(1450, 661),
    },

    {
    'pagina':6,
    'pos_xy':(870, 240),
    'curvado':False,
    'grafico':True,
    'grafico_tipo':'linha',
    'dados_do_grafico': [8, 20, 12, 23, 21],
    'tamanho_do_grafico':(811, 245),
    },

    {
    'pagina':6,
    'pos_xy':(870, 711),
    'curvado':False,
    'grafico':True,
    'grafico_tipo':'linha',
    'dados_do_grafico': [20, 28, 31, 40, 54],
    'tamanho_do_grafico':(811, 245),
    },

]




GERADOR_DE_APRESENTACAO(confg)