import unittest

from pyreutil.pyreutil import *

class TestReUtil(unittest.TestCase):
    
    def test_search_and_replace(self):
        regex_with_groups = "\[([\[]?[^\[^\]]+[\]]?)]\((http[s]?://[^\)]+)\)"
        sample_text = "In 1913,  [Ernst Zermelo](https://en.wikipedia.org/wiki/Ernst_Zermelo)  published *Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels* (*On an Application of Set Theory to the Theory of the Game of Chess*), which proved that the optimal chess strategy is  [strictly determined](https://en.wikipedia.org/wiki/Strictly_determined_game) . This paved the way for more general theorems. [[4]](https://en.wikipedia.org/wiki/Game_theory#cite_note-4) "
        
        self.assertRaises(TypeError, ReUtil().search_and_replace, regex=regex_with_groups, text=sample_text, replace="link", group=1)
        self.assertRaises(TypeError, ReUtil().search_and_replace, regex=regex_with_groups, text=sample_text)
        
        expected1 = "In 1913,  Ernst Zermelo  published *Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels* (*On an Application of Set Theory to the Theory of the Game of Chess*), which proved that the optimal chess strategy is  strictly determined . This paved the way for more general theorems. [4] "
        expected2 = "In 1913,  [link]  published *Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels* (*On an Application of Set Theory to the Theory of the Game of Chess*), which proved that the optimal chess strategy is  [link] . This paved the way for more general theorems. [link] "
        
        result1 = ReUtil().search_and_replace(regex_with_groups, sample_text, group=1)
        result2 = ReUtil().search_and_replace(regex_with_groups, sample_text, replace="[link]")
        self.assertEquals(expected1, result1)
        self.assertEquals(expected2, result2)
   
if __name__ == "__main__":
    unittest.main()
        