import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO

# Set no tema do seaborn para melhorar o visual dos plots
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Lendo os dados
@st.cache_data(show_spinner= True)
def load_data(file):
    try:
        return pd.read_csv(file, sep=';')
    except:
        return pd.read_excel(file)
    

# Função para filtragem
@st.cache_resource()
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)
    
# Função para converter o df para excel
@st.cache_data()
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    #writer.save()
    processed_data = output.getvalue()
    return processed_data




# Função Principal
def main():
    # Config inicial da página
    st.set_page_config(page_title = 'Telemarketing Analysis', \
                        page_icon = "telmarketing_icon.png",
                        layout='wide',
                        initial_sidebar_state='expanded')
    # Título
    st.write("# Telemarketing Analysis")
    st.markdown("---")

    # Apresenta a imagem na barra lateral da aplicação
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    # Botão para carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type = ['csv','xlsx'])

    if(data_file_1 is not None):
         bank_raw = load_data(data_file_1)
         bank = bank_raw.copy()

         st.write('## Antes dos filtros')
         st.write(bank.head())

         with st.sidebar.form(key = 'my_form'):
              # Seleciona tipo do gráfico
              graph_type = st.radio('Tipo de gráfico:', ('Barras','Pizza'))

              # Idade
              max_age = int(bank.age.max())
              min_age = int(bank.age.min())
              idades = st.slider(label='Idade', 
                                        min_value = min_age,
                                        max_value = max_age, 
                                        value = (min_age, max_age),
                                        step = 1)


              # Profissão
              jobs_list = bank.job.unique().tolist()
              jobs_list.append('all')
              jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

              # Estado civil
              marital_list = bank.marital.unique().tolist()
              marital_list.append('all')
              marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

              # Default?
              default_list = bank.default.unique().tolist()
              default_list.append('all')
              default_selected =  st.multiselect("Default", default_list, ['all'])

            
              # Financiamento imobiliário?
              housing_list = bank.housing.unique().tolist()
              housing_list.append('all')
              housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            
              # Empréstimo
              loan_list = bank.loan.unique().tolist()
              loan_list.append('all')
              loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])

            
              # Meio de contato
              contact_list = bank.contact.unique().tolist()
              contact_list.append('all')
              contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])

            
              # Mês de contato
              month_list = bank.month.unique().tolist()
              month_list.append('all')
              month_selected =  st.multiselect("Mês do contato", month_list, ['all'])

            
              # Dia da semana
              day_of_week_list = bank.day_of_week.unique().tolist()
              day_of_week_list.append('all')
              day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])


                    
              # encadeamento de métodos para filtrar a seleção
              bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                          .pipe(multiselect_filter, 'job', jobs_selected)
                          .pipe(multiselect_filter, 'marital', marital_selected)
                          .pipe(multiselect_filter, 'default', default_selected)
                          .pipe(multiselect_filter, 'housing', housing_selected)
                          .pipe(multiselect_filter, 'loan', loan_selected)
                          .pipe(multiselect_filter, 'contact', contact_selected)
                          .pipe(multiselect_filter, 'month', month_selected)
                          .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                    )

              submit_button = st.form_submit_button(label='Aplicar')

         # Download dos dados filtrados
         st.write("## Após filtros:")
         st.write(bank.head())

         st.download_button(label='Download tabela filtrada em Excel',
                            data = to_excel(bank),
                            file_name = 'bank_filtered.xlsx')
         
         # Fazendo as tabelas

         bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame()*100
         bank_raw_target_perc = bank_raw_target_perc.sort_index()
         bank_target_perc = bank.y.value_counts(normalize=True).to_frame()*100
         bank_target_perc = bank_target_perc.sort_index()

         col1, col2 = st.columns(2)

         col1.write("## Antes dos filtros: ")
         col1.write(bank_raw_target_perc)
         col1.download_button(label='Download',
                              data=to_excel(bank_raw_target_perc),
                              file_name='bank_perc.xlsx')
         col2.write("## Após os filtros: ")
         col2.write(bank_target_perc)
         col2.download_button(label='Download',
                              data=to_excel(bank_target_perc),
                              file_name='bank_filtered_perc.xlsx')
         
         st.markdown("---")
         
         # Gráficos

         st.write("## Proporção de aceite")

         fig, ax = plt.subplots(1,2, figsize = (5,3))

         if graph_type == 'Barras':
              sns.barplot(x = bank_raw_target_perc.index, 
                        y = 'proportion',
                        data = bank_raw_target_perc, 
                        ax = ax[0])
              ax[0].set_title('Antes dos filtros')
              ax[0].bar_label(ax[0].containers[0])
              sns.barplot(data=bank_target_perc,
                          x=bank_target_perc.index,
                          y='proportion',
                          ax=ax[1])
              ax[1].set_title('Após filtragem')
              ax[1].bar_label(ax[1].containers[0])
              
         else:
             bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='proportion', ax = ax[0], legend=False, ylabel='')
             ax[0].set_title('Antes dos filtros')
            
             bank_target_perc.plot(kind='pie', autopct='%.2f', y='proportion', ax = ax[1], legend=False, ylabel='')
             ax[1].set_title('Após filtragem')





         st.pyplot(plt)









if __name__ == '__main__':
	main()
