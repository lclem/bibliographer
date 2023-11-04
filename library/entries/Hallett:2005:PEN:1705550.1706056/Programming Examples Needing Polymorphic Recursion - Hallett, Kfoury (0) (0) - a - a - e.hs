
{-# OPTIONS_GHC -XScopedTypeVariables #-}

intFunc :: Int -> Int
intFunc x = x + 1

doubleFunc :: Double -> Double
doubleFunc x = sqrt x

-- it does not type-check since twice is polymorphic and used in a recursion
--myPair = let (twice, foo, goo) = (\f y -> f (f y),
--                                  \v -> twice intFunc v,
--                                  \w -> twice doubleFunc w)
--         in (foo 3, goo 16.0)

-- this works since "twice" has been uncoupled from the recursion
myPair' = let twice = \f y -> f (f y) in
          let (foo, goo) = (\v -> twice intFunc v,
                           \w -> twice doubleFunc w)
                           in (foo 3, goo 16.0)

sum = let id = \x -> x
          sumList [] = 0
          sumList (x:xs) = id x + sumList (id xs)
      in sumList [1,2,3]

twice :: forall a . (a -> a) -> a -> a
twice f x = f $ f x

k :: a -> (forall b . (b -> a))
k x y = x

--twice_k = twice k
-- error:
--    Occurs check: cannot construct the infinite type: a0 = b0 -> a0
--    Expected type: a0 -> a0
--    Actual type: a0 -> b0 -> a0
--    In the first argument of `twice', namely `k'
--    In the expression: twice k

twice_k' = let f = k in \x -> f $ f x

f x = x id