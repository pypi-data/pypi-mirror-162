from expr import Parser
import unittest
    
class ExprTest(unittest.TestCase):
    
    parser = Parser()

    def test_exists(self):
        expr = self.parser.parse('a/topic exists')
        self.assertEqual(len(expr.keys), 1)
        self.assertTrue(expr({ 'a/topic' : 1 }))
        self.assertFalse(expr({}))

    def test_less(self):
        expr = self.parser.parse('a/topic < 1')
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 1 }))
        self.assertFalse(expr({ 'a/topic' : '1' }))
        self.assertTrue(expr({ 'a/topic' : 0 }))
        self.assertTrue(expr({ 'a/topic' : '0' }))
        self.assertRaises(KeyError, expr, {})
        self.assertRaises(ValueError, expr, { 'a/topic' : 'foo' })

    def test_less_equal(self):
        expr = self.parser.parse('a/topic <= 1')
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 2 }))
        self.assertFalse(expr({ 'a/topic' : '2' }))
        self.assertTrue(expr({ 'a/topic' : 1 }))
        self.assertTrue(expr({ 'a/topic' : '1' }))
        self.assertRaises(KeyError, expr, {})
        self.assertRaises(ValueError, expr, { 'a/topic' : 'foo' })

    def test_greater_equal(self):
        expr = self.parser.parse('a/topic >= 1')
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 0 }))
        self.assertFalse(expr({ 'a/topic' : '0' }))
        self.assertTrue(expr({ 'a/topic' : 1 }))
        self.assertTrue(expr({ 'a/topic' : '1' }))
        self.assertRaises(KeyError, expr, {})
        self.assertRaises(ValueError, expr, { 'a/topic' : 'foo' })

    def test_greater(self):
        expr = self.parser.parse('a/topic > 1')
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 1 }))
        self.assertFalse(expr({ 'a/topic' : '1' }))
        self.assertTrue(expr({ 'a/topic' : 2 }))
        self.assertTrue(expr({ 'a/topic' : '2' }))
        self.assertRaises(KeyError, expr, {})
        self.assertRaises(ValueError, expr, { 'a/topic' : 'foo' })

    def test_equal_number(self):
        expr = self.parser.parse('a/topic == 1')
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 0 }))
        self.assertFalse(expr({ 'a/topic' : '0' }))
        self.assertTrue(expr({ 'a/topic' : 1 }))
        self.assertTrue(expr({ 'a/topic' : '1' }))
        self.assertRaises(KeyError, expr, {})
        self.assertRaises(ValueError, expr, { 'a/topic' : 'foo' })

    def test_equal_string(self):
        expr = self.parser.parse("a/topic == '1'")
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : '' }))
        self.assertTrue(expr({ 'a/topic' : '1' }))
        self.assertTrue(expr({ 'a/topic' : 1 }))
        self.assertRaises(KeyError, expr, {})

    def test_not_equal_number(self):
        expr = self.parser.parse('a/topic != 1')
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 1 }))
        self.assertFalse(expr({ 'a/topic' : '1' }))
        self.assertTrue(expr({ 'a/topic' : 0 }))
        self.assertTrue(expr({ 'a/topic' : '0' }))
        self.assertRaises(KeyError, expr, {})
        self.assertRaises(ValueError, expr, { 'a/topic' : 'foo' })

    def test_not_equal_string(self):
        expr = self.parser.parse("a/topic != '1'")
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : '1' }))
        self.assertTrue(expr({ 'a/topic' : '' }))
        self.assertTrue(expr({ 'a/topic' : 0 }))
        self.assertRaises(KeyError, expr, {})

    def test_and(self):
        expr = self.parser.parse("a/topic == 1 and b/topic == 2")
        self.assertEqual(len(expr.keys), 2)
        self.assertTrue(expr({ 'a/topic' : 1, 'b/topic' : 2 }))
        self.assertFalse(expr({ 'a/topic' : 0, 'b/topic' : 2 }))
        self.assertFalse(expr({ 'a/topic' : 1, 'b/topic' : 0 }))
        self.assertRaises(KeyError, expr, {})

    def test_or(self):
        expr = self.parser.parse("a/topic == 1 or b/topic == 2")
        self.assertEqual(len(expr.keys), 2)
        self.assertTrue(expr({ 'a/topic' : 1, 'b/topic' : 1 }))
        self.assertTrue(expr({ 'a/topic' : 0, 'b/topic' : 2 }))
        self.assertFalse(expr({ 'a/topic' : 0, 'b/topic' : 0 }))
        self.assertRaises(KeyError, expr, {})

    def test_not(self):
        expr = self.parser.parse("not a/topic == 1")
        self.assertEqual(len(expr.keys), 1)
        self.assertFalse(expr({ 'a/topic' : 1 }))
        self.assertTrue(expr({ 'a/topic' : 2 }))
        self.assertRaises(KeyError, expr, {})

    def test_precedence(self):
        expr = self.parser.parse("b/topic == 1 and a/topic == 2 or a/topic == 3 and b/topic == 4")
        self.assertEqual(len(expr.keys), 2)
        self.assertTrue(expr({ 'a/topic' : 2, 'b/topic' : 1 }))
        self.assertTrue(expr({ 'a/topic' : 3, 'b/topic' : 4 }))
        self.assertFalse(expr({ 'a/topic' : 2, 'b/topic' : 3 }))

    def test_parenthesis(self):
        expr = self.parser.parse("a/topic == 1 and (b/topic == 2 or b/topic == 3)")
        self.assertEqual(len(expr.keys), 2)
        self.assertTrue(expr({ 'a/topic' : 1, 'b/topic' : 2 }))
        self.assertTrue(expr({ 'a/topic' : 1, 'b/topic' : 3 }))

if __name__ == '__main__': unittest.main()
