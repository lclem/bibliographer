A program inspired by
What Sequential Games, the Tychonoff Theorem
and the Double-Negation Shift have in Common
by Martin Escardo and Paulo Oliva

Philip Wadler, 30 Aug 2010 (revised 31 Aug 2010)


A recent paper by Escardo and Oliva [1], to appear in MSFP 2010,
relates diverse aspects of computing, in the form of a literate
Haskell program.  This note is inspired by theirs, and is also a
literate Haskell program.  It improves on theirs in a few ways,
notably by using type classes to characterize valuation types, and by
using QuickCheck to describe and check relevant properties.  This
note can be read stand-alone, but is best read in conjunction with
Escardo and Oliva's paper.

The starting point is finding optimal elements of sets.  Let (J a)
represent a non-empty collection of values of type a.  Let r be a
valuation type equipped with binary operation `sup` which selects the
larger of its two arguments.

  class Sup r where
    sup :: r -> r -> r

Using Haskell type classes, we write Sup r to indicate that type r
must support a binary operation `sup`.  Escardo and Oliva restrict
attention to a few specific instances of r; an advantage of the
development here is that we use type classes to generalize to any r
with a suitable supremum operator.

Presume we are given a valuation function k :: a -> r which takes
elements of the set into valuations.  We are interested in an
operation optimum, which picks the element with the largest valuation.

  optimum :: Sup r => J a -> (a -> r) -> a

We require the collection to be non-empty so that there is always such
an element.

Given optimum, it is easy to define an operation supremum that finds
the largest valuation of any element in the set.

  supremum :: Sup r => J a -> (a -> r) -> r
  supremum x k  =  k (optimum x k)

The definition of supremum may seem roundabout: first compute the
element which under the evaluation function returns a dominant value,
and then apply the evaluation function.  But this roundabout approach
is the key to ensuring that supremum is defined even on infinite sets.

Escardo and Oliva take this simple idea in a number of directions.  If
r is Bool and `sup` is disjunction, then k is a predicate (a map from
elements to booleans), and supremum corresponds to the existential
quantifier (it returns true when there is an element in the set that
satisfies the predicate).  Further, optimum corresponds to Hilbert's
epsilon operator, which selects an element of a set satisfying the
predicate if one exists, and returns an arbitrary element otherwise.

They observe it is possible to represent sets by choosing (J a)
to correspond to the type of the supremum operation.

  newtype J a = J (forall r. Sup r => (a->r)->a)

Escardo and Oliva use a formalism that ties a set to a specific
valuation type r, defining J r a = (a->r)->a; an advantage of the
development here is that we define sets that work with any suitable
valuation type.

They observe that J has the structure of a monad, and hence that the
standard sequence operator over monads can then be used to convert a
value of type [J a] to a value of type J [a], that is, to convert a
list of sets to a set of lists.  They further observe that,
remarkably, this construct works even when the list is an infinite
stream.

In particular, one can construct a set that represents all possible
infinite sequences of booleans (also known as the Cantor Set), and
find an optimum over this infinite set in finite time.  Recall how
supremum was defined by applying the evaluator to the optimum.  Over
cantor sets optimum will converge (but not arrive) on an optimum
infinite stream; but the evaluator k will only look at a finite number
of elements of the infinite stream, and so can yield a value.  They
observe that this construct corresponds to the computational content
of Tychonoff's theorem in topology.  As an application, they define
computable equality for certain classes of functionals.

They also define the related type

  newtype K a = K (forall r. Sup r => (a->r)->r)

which is derived from J by by replacing the final a with an r.  They
observe this also corresponds to a monad, known as the continuation
monad.  It is well-known that viewed through the lens of
propositions-as-types that K corresponds to the double-negation
translation in logic.  They further observe that viewed through this
same lens, the type J a is related to Peirce's law.


Preliminaries
~~~~~~~~~~~~~

Our program uses some extensions over Haskell.  We use rank 2 types
in order to permit quantifying over r in the definitions of J and K.
We also use multi-parameter type classes to classify functions that
are representable by elements of the Cantor Set, and we import a few
standard library functions and the QuickCheck library.

> {-# LANGUAGE Rank2Types, MultiParamTypeClasses #-}
> import Monad(join)
> import Test.QuickCheck
> import Text.Show.Functions


Conventions
~~~~~~~~~~~

Let a, b range over arbitrary types, and values of such types.  Let x,
y range over sets (or more generally monads), and phi range over sets
of sets (or more generally a monad of monads).  Let r,s range over
types that support a sup operator, and values of such types.


Outcomes
~~~~~~~~

An outcome of a game may be to lose, win, or draw.

> data Outcome = Lose | Draw | Win deriving (Eq,Ord,Enum,Bounded,Show)

In what follows, running examples use Booleans, integers,
and outcomes.


Sup
~~~

We require a binary operator `sup` that finds the supremum of two
elements.

> class Eq r => Sup r where
>   sup :: r -> r -> r

> instance Sup Bool where
>   r `sup` s  =  r || s

> instance Sup Int where
>   r `sup` s  =  r `max` s

> instance Sup Outcome where
>   Win  `sup` r  =  Win
>   Draw `sup` r  =  Draw `max` r
>   Lose `sup` r  =  r

Operator `sup` differs from `max` in that it is lazy in its
second argument where possible.

  *Main> True `sup` undefined
  True
  *Main> True `max` undefined
  *** Exception: Prelude.undefined
  *Main> Win `sup` undefined
  Win
  *Main> Win `max` undefined
  *** Exception: Prelude.undefined

However, `sup` is equivalent to `max` for all defined values.

> prop_max :: (Sup r, Ord r) => r -> r -> Bool
> prop_max r s  =  (r `sup` s) == (r `max` s)

> check_max =
>   quickCheck (prop_max :: Bool -> Bool -> Bool) >>
>   quickCheck (prop_max :: Int -> Int -> Bool) >>
>   quickCheck (prop_max :: Outcome -> Outcome -> Bool)

We intend to select an optimum element from a set---an element whose
image under a given evaluation function is the supremum.  Therefore,
one property we require of `sup` is that it returns one of its
arguments.

> prop_atomic :: Sup r => r -> r -> Bool
> prop_atomic r s  =  (r `sup` s == r) || (r `sup` s == s)

> check_atomic =
>   quickCheck (prop_atomic :: Bool -> Bool -> Bool) >>
>   quickCheck (prop_atomic :: Int -> Int -> Bool) >>
>   quickCheck (prop_atomic :: Outcome -> Outcome -> Bool)

Observe that we do not have the following instance

  instance (Sup r, Sup s) => Sup (r,s) where
    (r,s) `sup` (t,u) = (r `sup` t, s `sup` u)

since it violates the above property.  For instance, (1,2) `sup` (4,3)
is (2,4) which equals neither (1,2) nor (4,3).  In particular, this
means that not every Boolean algebra belongs to Sup.  It would be
interesting to classify algebraically the properties Sup must satisfy.


Partial order
~~~~~~~~~~~~~

From the `sup` operator we infer a partial order.

> dominates :: Sup r => r -> r -> Bool
> r `dominates` s  =  r == (r `sup` s)

Operator `dominates` differs from (>=) in that it is lazy in its
second argument where possible.

  *Main> True `dominates` undefined
  True
  *Main> True >= undefined
  *** Exception: Prelude.undefined
  *Main> Win `dominates` undefined
  True
  *Main> Win >= undefined
  *** Exception: Prelude.undefined

However, `dominates` is equivalent to (>=) for all defined values.

> prop_geq :: (Sup r, Ord r) => r -> r -> Bool
> prop_geq r s  =  (r `dominates` s) == (r >= s)

> check_geq =
>   quickCheck (prop_geq :: Bool -> Bool -> Bool) >>
>   quickCheck (prop_geq :: Int -> Int -> Bool) >>
>   quickCheck (prop_geq :: Outcome -> Outcome -> Bool)


Negation
~~~~~~~~

Sometimes we want to compute the smallest value rather than the
largest.  We do so using an involutive negation operator and
deMorgan duality.

> class Sup r => Neg r where
>   neg :: r -> r

> instance Neg Bool where
>   neg = not

> instance Neg Int where
>   neg r = -r

> instance Neg Outcome where
>   neg Win  = Lose
>   neg Draw = Draw
>   neg Lose = Win

Negation is an involution.

> prop_involution :: Neg r => r -> Bool
> prop_involution r  =  neg (neg r) == r

> check_involution =
>   quickCheck (prop_involution :: Bool -> Bool) >>
>   quickCheck (prop_involution :: Int -> Bool) >>
>   quickCheck (prop_involution :: Outcome -> Bool)

We define duality for binary operators.

> dual :: Neg r => (r -> r -> r) -> (r -> r -> r)
> dual op r s  =  neg (neg r `op` neg s)

The infimum is the dual of the supremum.

> inf :: Neg r => r -> r -> r
> inf  =  dual sup

DeMorgan's law is the special case of this where r is Bool, `sup` is
disjunction, `inf` is conjunction, and neg is complement.

> prop_conjunction :: Bool -> Bool -> Bool
> prop_conjunction r s  =  (r `inf` s) == (r && s)

> check_conjunction = quickCheck prop_conjunction

Just as `sup` is equivalent to `max` for defined values,
so is `inf` equivalent to `min`.

> prop_min :: (Neg r, Ord r) => r -> r -> Bool
> prop_min r s  =  (r `inf` s) == (r `min` s)

> check_min =
>   quickCheck (prop_min :: Bool -> Bool -> Bool) >>
>   quickCheck (prop_min :: Int -> Int -> Bool) >>
>   quickCheck (prop_min :: Outcome -> Outcome -> Bool)

Negation is not necessarily a complement in the sense of Boolean
algebra.  A complement should satisfy the property that
(a `sup` neg a) dominates every other value.  This is satisfied
by Bool, but not by Int or Outcome.  Again, it would be interesting to
classify algebraically the properties Neg must satisfy.


Optimum monad
~~~~~~~~~~~~~

Above, we motivated the definition of a type (J a), which can be
used to represent non-empty sets with elements of type a.

> newtype J a = J { unJ :: forall r. Sup r => (a -> r) -> a }

We require that a `sup` operation be available on the valuation
type r.  It turns out that this is not required for the monad
structure, but it is required for the `union` operation that we
define below.

> instance Monad J where
>   return a  =  J (\k -> a)
>   x >>= f   =  J (\k -> unJ (f (unJ x (\a -> k (unJ (f a) k)))) k)

Escardo and Oliva define (>>=) in terms of fmap and join, called
functorJ and muJ.  We can compute their definitions from ours; their
definition refers to the function 'overline' defined below.  As
required, we have

    fmap f
  =
    x >>= (return . f)
  =
    J (\k -> unJ (return (f (unJ x (\a -> k (unJ (return (f a)) k)))) k)
  =
    J (\k -> f (unJ x (\a -> k (f a))))
  =
    J (\k -> f (unJ x (k . f)))

and

    join phi
  =
    phi >>= id
  =
    J (\k -> unJ (id (unJ phi (\x -> k (unJ (id x) k)))) k)
  =
    J (\k -> unJ (unJ phi (\x -> k (unJ x k))) k)
  =
    J (\k -> unJ (unJ phi (\x -> unK (overline x) k)) k)


Supremum monad
~~~~~~~~~~~~~~

We also motivated the definition of a type (K a), which 
is identical to the continuation monad, save that again we
restrict attention to valuation types with a `sup` operation.

> newtype K a = K { unK :: forall r. Sup r => (a -> r) -> r }

This has a well-known monadic structure.

> instance Monad K where
>   return a  =  K (\k -> k a)
>   x >>= f   =  K (\k -> unK x (\a -> unK (f a) k))

Again, Escardo and Oliva define (>>=) using fmap and join, called
functorJ and muJ.  We can compute their definitions from ours.

    fmap f x
  =
    x >>= (return . f)
  =
    K (\k -> unK x (\a -> unK (return (f a)) k))
  =
    K (\k -> unK x (\a -> k (f a)))
  =
    K (\k -> unK x (k . f))

and

    join phi
  =
    phi >>= id
  =
    K (\k -> unK phi (\x -> unK (id x) k))
  =
    K (\k -> unK phi (\x -> unK x k))


Monad morphism
~~~~~~~~~~~~~~

There is a monad morphism between the two monads.

> overline :: J a -> K a
> overline x = K (\k -> k (unJ x k))


Sets
~~~~

We extend the optimum monad with union, giving it a set structure.  It
is in order to define union that we require Sup r in the definition of
J and K.

> union :: J a -> J a -> J a
> x `union` y  =  J (\k -> let a = unJ x k in
>                          let b = unJ y k in
>                          if k a `dominates` k b then a else b)

Singleton is the same as the return of the monad, and doubleton is the
union of two singletons.

> singleton :: a -> J a
> singleton = return

> doubleton :: a -> a -> J a
> a `doubleton` b = singleton a `union` singleton b

More generally, is straightforward to convert a non-empty list into a set.
This is the monad morphism from the list monad to J.

> set :: [a] -> J a
> set =  foldr1 union . map return

The function 'set' is called 'argsup' in the paper (end of Section
2.2).  Note that with our definition of `sup` for Outcome, that 'set'
behaves just like the version of 'argsup' optimized for evaluation
functions that yield -1, 0, or 1 given in the paper.

The J monad finds an optimum (an element of the set with the largest
value under the provided function), and from this we may define the
supremum (the largest value under the provided function).

> optimum :: Sup r => J a -> (a -> r) -> a
> optimum =  unJ

> supremum :: Sup r => J a -> (a -> r) -> r
> supremum x k =  k (optimum x k)


Pessimum and infimum are the duals of optimum and supremum.

> pessimum :: Neg r => J a -> (a -> r) -> a
> pessimum x k  =  optimum x (neg . k)

> infimum :: Neg r => J a -> (a -> r) -> r
> infimum x k  =  neg (supremum x (neg . k))

Existential and universal quantifiers are a special case of
supremum and infimum.

> forsome :: J a -> (a -> Bool) -> Bool
> forsome =  supremum

> forevery :: J a -> (a -> Bool) -> Bool
> forevery =  infimum

Set membership is a special case of the existential.

> member :: (Eq a) => a -> J a -> Bool
> a `member` x  =  forsome x (== a)

It is easy to define the set containing false and true, and the Cantor
Set containing every infinite sequence of booleans.

> bit :: J Bool
> bit = set [False,True]

> cantor :: J [Bool]
> cantor = sequence (repeat bit)


Some checks
~~~~~~~~~~~

We check that supremum and infimum behave as expected.

> prop_supremum :: Sup r => (a -> r) -> [a] -> Property
> prop_supremum k x  =  not (null x) ==>
>                         (supremum (set x) k == foldr1 sup (map k x))

> check_supremum =
>   quickCheck (prop_supremum :: (Int -> Int) -> [Int] -> Property) >>
>   quickCheck (prop_supremum :: (Int -> Outcome) -> [Int] -> Property) >>
>   quickCheck (prop_supremum :: (Outcome -> Int) -> [Outcome] -> Property) >>
>   quickCheck (prop_supremum :: (Outcome -> Outcome) -> [Outcome] -> Property)

> prop_infimum :: Neg r => (a -> r) -> [a] -> Property
> prop_infimum k xs  =  not (null xs) ==>
>                         (infimum (set xs) k == foldr1 inf (map k xs))

> check_infimum =
>   quickCheck (prop_infimum :: (Int -> Int) -> [Int] -> Property) >>
>   quickCheck (prop_infimum :: (Int -> Outcome) -> [Int] -> Property) >>
>   quickCheck (prop_infimum :: (Outcome -> Int) -> [Outcome] -> Property) >>
>   quickCheck (prop_infimum :: (Outcome -> Outcome) -> [Outcome] -> Property)

And, in particular, we check that forall, forsome, and member on sets
are equivalent to the standard operations on lists.

> prop_forsome :: (a -> Bool) -> [a] -> Property
> prop_forsome k x  =  not (null x) ==> (forsome (set x) k == any k x)

> check_forsome =
>   quickCheck (prop_forsome :: (Int -> Bool) -> [Int] -> Property) >>
>   quickCheck (prop_forsome :: (Outcome -> Bool) -> [Outcome] -> Property)

> prop_forevery :: (a -> Bool) -> [a] -> Property
> prop_forevery k x  =  not (null x) ==> (forevery (set x) k == all k x)

> check_forevery =
>   quickCheck (prop_forevery :: (Int -> Bool) -> [Int] -> Property) >>
>   quickCheck (prop_forevery :: (Outcome -> Bool) -> [Outcome] -> Property)

> prop_member :: (Eq a) => a -> [a] -> Property
> prop_member a x  =  not (null x) ==> ((a `member` set x) == (a `elem` x))

> check_member =
>   quickCheck (prop_member :: Int -> [Int] -> Property) >>
>   quickCheck (prop_member :: Outcome -> [Outcome] -> Property)


Naturals
~~~~~~~~

We introduce naturals, which we use as indexes to streams.

> newtype Nat = Nat Int deriving (Eq,Ord,Show)

> (!!!) :: [a] -> Nat -> a
> x !!! (Nat n)  =  x !! n

> instance Num Nat where
>   Nat m + Nat n  =  Nat (m+n)
>   Nat m * Nat n  =  Nat (m*n)
>   Nat m - Nat n | m >= n  =  Nat (m-n)
>   fromInteger n | n >= 0  =  Nat (fromInteger n)
>   abs = undefined
>   signum = undefined

> instance Enum Nat where
>   toEnum n | n >= 0  =  Nat n
>   fromEnum (Nat n)   =  n


Fan functional
~~~~~~~~~~~~~~

Given a function over streams of Booleans, the fan functional
determines the least position past which the arguments of the function
are not examined.

> fan :: Eq r => ([Bool] -> r) -> Nat
> fan f  =  least (\ (Nat n) ->
>             forevery cantor (\x -> 
>               forevery cantor (\y ->
>                 (take n x == take n y) --> (f x == f y))))

> least :: (Nat -> Bool) -> Nat
> least p  =  head [ i | i <- [0..], p i ]

> (-->) :: Bool -> Bool -> Bool
> p --> q  =  not p || q

An alternative definition of the fan functional, from Ulrich
Berger's thesis (1990):

> fan2 :: Eq r => ([Bool] -> r) -> Nat
> fan2 f = if forevery cantor (\x -> f x == f (repeat False))
>          then 0
>          else 1 + max (fan2 (f.(False:))) (fan2 (f.(True:)))

Given a list of naturals, we can generate a function that examines its
argument at the specified positions, and use this to check fan.  In
order for the test to complete in reasonable time, we restrict
ourselves to short lists of small naturals, using the Quick Check
function 'resize'.

> examineAt :: [Nat] -> [Bool] -> Bool
> examineAt ns x  =  and [ x !!! n | n <- ns ]

> prop_fan :: (([Bool] -> Bool) -> Nat) -> Gen [Nat] -> Property
> prop_fan fan gen  =  forAll gen (\ns -> 
>                        fan (examineAt ns) == foldr max 0 [ n + 1 | n <- ns])

> check_fan  = quickCheck (prop_fan fan  (resize 4 arbitrary))
> check_fan2 = quickCheck (prop_fan fan2 (resize 4 arbitrary))

We can also check that the two functionals are equivalent.

> prop_equal_fan :: Gen [Nat] -> Property
> prop_equal_fan gen  =  forAll gen (\ns -> 
>                         fan (examineAt ns) == fan2 (examineAt ns))

> check_equal_fan = quickCheck (prop_equal_fan (resize 4 arbitrary))

In this case, it would be better to generate functions directly rather
than generate a list and apply examineAt.  However, doing so causes
QuickCheck to loop, because coarbitrary for lists examines too much of
its input.


Equality for functionals
~~~~~~~~~~~~~~~~~~~~~~~~

We call a function type a -> b representable if every function of
the type can be generated from a stream of Booleans.  In particular,
the function type Int -> Bool is representable.  We use 'interleave',
the standard mapping of integers to naturals.

> interleave :: Int -> Nat
> interleave i | i >= 0  =  Nat (2*i)
>              | i < 0   =  Nat (2*(-i)-1)

> class Representable a b where
>   decode :: [Bool] -> (a -> b)

> instance Representable Int Bool where
>   decode x i  =  x !!! interleave i

> instance Representable Nat Bool where
>   decode x i  =  x !!! i

Equality is decidable for any functional of type (a->b)->c where a->b
is representable and c has equality.

> equal :: (Representable a b, Eq c) => ((a->b)->c) -> ((a->b)->c) -> Bool
> equal f g  =  forevery cantor (\x -> f (decode x) == g (decode x))

We check that equality is reflexive.

> prop_reflexive :: (Representable a b, Eq c) => Gen ((a->b)->c) -> Property
> prop_reflexive gen =
>   forAll gen (\f -> equal f f)

> check_reflexive =
>   quickCheck (prop_reflexive (resize 5 arbitrary :: Gen ((Int->Bool)->Outcome)))

We check that two arbitrary functions are either equal (in which case
they should have the same value on arbitrary arguments) or unequal (in
which case we can search the cantor space for a counterexample on
which they are unequal).  We use the QuickCheck function 'resize' to
restrict our attention to small cases, and 'label' to indicate how
many random tests fall under each case.

> prop_equal :: (Representable a b, Eq c) => Gen ((a->b)->c) -> Gen (a->b) -> Property
> prop_equal gen gen2 =
>   forAll gen (\f ->
>     forAll gen (\g ->
>       if (equal f g) then
>         forAll gen2 (\a ->
>           label "equal" (f a == g a))
>       else
>         let a = decode (optimum cantor (\x -> f (decode x) /= g (decode x))) in
>           label "unequal" (f a /= g a)))

> check_equal =
>   quickCheck (prop_equal (resize 8 arbitrary :: Gen ((Int->Bool)->Outcome))
>                          (resize 8 arbitrary :: Gen (Int->Bool)))


Run all checks
~~~~~~~~~~~~~~

For convenience, here is a function that runs all checks.

> main = 
>   check_max >>
>   check_atomic >>
>   check_geq >>
>   check_involution >>
>   check_conjunction >>
>   check_min >>
>   check_supremum >>
>   check_infimum >>
>   check_forsome >>
>   check_forevery >>
>   check_member >>
>   check_fan >>
>   check_fan2 >>
>   check_equal_fan >>
>   check_reflexive >>
>   check_equal


Efficiency
~~~~~~~~~~

An earlier version defined `union` in terms of `doubleton`, rather
than the other way around.

> doubleton2 :: a -> a -> J a
> a `doubleton2` b  =  J (\k -> if k a `dominates` k b then a else b)

> union2 :: J a -> J a -> J a
> x `union2` y  =  join (x `doubleton2` y)

> set2 :: [a] -> J a
> set2 =  foldr1 union2 . map singleton

It is easy to check that this is equivalent, though less efficient.

    x `union2` y
  =
    join (x `doubleton2` y)
  =
    J (\k -> unJ (unJ (x `doubleton` y) (\x -> k (unJ x k))) k) 
  =
    J (\k -> unJ ((\k -> if k x `dominates` k y then x else y) (\x -> k (unJ x k))) k)
  =
    J (\k -> unJ (if k (unj x k) `dominates` k (unJ x k) then x else y) k)
  =
    J (\k -> if k (unj x k) `dominates` k (unJ x k) then unj x k else unj y k)

The loss of efficiency turns out to be exponential---while the
supremum of a list of length 24 can be computed too fast to notice
using set, using set2 it takes about half a minute.  For a list
of length 25, it takes twice as long.

  *Main> :set +s
  *Main> supremum (set [0..23]) id :: Int
  23
  (0.00 secs, 525096 bytes)
  *Main> supremum (set2 [0..23]) id :: Int
  23
  (30.10 secs, 3192968796 bytes)
  *Main> supremum (set [0..24]) id :: Int
  24
  (0.00 secs, 525092 bytes)
  *Main> supremum (set2 [0..24]) id :: Int
  24
  (60.19 secs, 6385879616 bytes)



Appendix: QuickCheck support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To support testing with QuickCheck, we define instances
of Arbitrary and CoArbitrary for Outcome and Naturals.

> instance Arbitrary Outcome where
>   arbitrary = oneof (map return [Lose, Draw, Win])

> instance CoArbitrary Outcome where
>   coarbitrary o  = variant (fromEnum o)

> instance Arbitrary Nat where
>   arbitrary = sized (\ n -> do m <- choose (0,n)
>                                return (Nat m))

> instance CoArbitrary Nat where
>   coarbitrary (Nat n) = variant n


Acknowledgements
~~~~~~~~~~~~~~~~

Thanks for their comments to Lennart Augustsson, Martin Escardo,
Kenneth MacKenzie, James McKenna, Paulo Oliva, and Kalani Thielen.


References
~~~~~~~~~~

[1] Martin Escardo and Paulo Oliva, What Sequential Games, the
Tychonoff Theorem and the Double-Negation Shift have in Common,
MSFP 2010.

(Additional reference, added 3 Dec 2010)

[2] Martin Escardo and Paulo Oliva, Sequential Games and optimal
strategies, Proceedings of the Royal Society A, published online 1
December 2010, doi: 10.1098/rspa.2010.0471.
http://rspa.royalsocietypublishing.org/content/early/2010/11/26/rspa.2010.0471