import unittest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import substitui_nulos, corrigir_erros_digitacao, tratar_outliers

class TestUtils(unittest.TestCase):
    """Testes para funções utilitárias"""
    
    def setUp(self):
        """Configuração dos dados de teste"""
        self.df_test = pd.DataFrame({
            'coluna_numerica': [1, 2, None, 4, 100],  # Outlier: 100
            'coluna_categorica': ['A', 'B', None, 'C', 'Aa']  # Erro digitação: 'Aa'
        })
        
        self.lista_valida = ['A', 'B', 'C', 'D']
    
    def test_substitui_nulos(self):
        """Testa substituição de valores nulos"""
        df_copy = self.df_test.copy()
        substitui_nulos(df_copy)
        
        # Verifica se não há mais nulos
        self.assertFalse(df_copy.isnull().any().any())
        
        # Verifica se a mediana foi usada para coluna numérica
        self.assertEqual(df_copy.loc[2, 'coluna_numerica'], 2.0)  # mediana de [1,2,4,100]
    
    def test_corrigir_erros_digitacao(self):
        """Testa correção de erros de digitação"""
        df_copy = self.df_test.copy()
        corrigir_erros_digitacao(df_copy, 'coluna_categorica', self.lista_valida)
        
        # Verifica se 'Aa' foi corrigido para 'A'
        self.assertEqual(df_copy.loc[4, 'coluna_categorica'], 'A')
    
    def test_tratar_outliers(self):
        """Testa tratamento de outliers"""
        df_copy = self.df_test.copy()
        df_resultado = tratar_outliers(df_copy, 'coluna_numerica', 0, 50)
        
        # Verifica se outlier (100) foi substituído pela mediana
        mediana_esperada = df_copy[(df_copy['coluna_numerica'] >= 0) & 
                                  (df_copy['coluna_numerica'] <= 50)]['coluna_numerica'].median()
        self.assertEqual(df_resultado.loc[4, 'coluna_numerica'], mediana_esperada)

class TestModelValidation(unittest.TestCase):
    """Testes para validação do modelo"""
    
    def setUp(self):
        """Dados de teste para validação do modelo"""
        self.sample_data = {
            'profissao': ['Advogado'],
            'tempoprofissao': [5],
            'renda': [10000.0],
            'tiporesidencia': ['Própria'],
            'escolaridade': ['Superior'],
            'score': ['Bom'],
            'idade': [35],
            'dependentes': [2],
            'estadocivil': ['Casado'],
            'produto': ['EcoPrestige'],
            'valorsolicitado': [50000.0],
            'valortotalbem': [100000.0],
            'proporcaosolicitadototal': [0.5]
        }
    
    def test_data_format(self):
        """Testa se os dados estão no formato correto"""
        df = pd.DataFrame(self.sample_data)
        
        # Verifica tipos de dados
        self.assertIsInstance(df['renda'].iloc[0], float)
        self.assertIsInstance(df['idade'].iloc[0], (int, np.integer))
        self.assertIsInstance(df['profissao'].iloc[0], str)
    
    def test_data_ranges(self):
        """Testa se os dados estão dentro dos ranges esperados"""
        df = pd.DataFrame(self.sample_data)
        
        # Testa ranges
        self.assertGreater(df['idade'].iloc[0], 18)
        self.assertLess(df['idade'].iloc[0], 100)
        self.assertGreaterEqual(df['dependentes'].iloc[0], 0)
        self.assertGreaterEqual(df['proporcaosolicitadototal'].iloc[0], 0)
        self.assertLessEqual(df['proporcaosolicitadototal'].iloc[0], 1)

if __name__ == '__main__':
    # Cria diretório de logs se não existir
    os.makedirs('./logs', exist_ok=True)
    
    # Executa os testes
    unittest.main(verbosity=2)
