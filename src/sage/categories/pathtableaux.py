"""
This is a category for using local rules to construct rectification
and the action of the cactus group. This is an effective version
of the Henriques-Kamnitzer construction of the action of the cactus
group on tensor powers of a crystal. This is a generalisation of
the Fomin growth rules which are an effective version of the operations
on standard tableaux which were previously constructed using jeu-de-taquin.

The basic operations are rectification, evacuation and promotion.
Rectification of standard skew tableaux agrees with the rectification
by jeu-de-taquin as does evacuation. Promotion agrees with promotion
by jeu-de-taquin on rectangular tableaux but in general they are different.

AUTHORS:

- Bruce Westbury (2018): initial version

#*****************************************************************************
#       Copyright (C) 2018 Bruce Westbury <bruce.westbury@gmail.com>,
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************


"""


from sage.misc.abstract_method import abstract_method
from sage.categories.category import Category
from sage.categories.sets_cat import Sets

class PathTableaux(Category):
    """
    This defines the category of PathTableaux.
    """
    def super_categories(self):
        return [Sets()]

    class ElementMethods:
        """
        These methods are not called directly. Instead, when a Element class
        for this Category is created these methods are automatically added
        to the class methods.
        """

############################ Abstract Methods #################################

        @abstract_method(optional=False)
        def check(self):
            """
            This is an abstract method. It must be overwritten in any
            Element class for this Category. Typically an instance of
            an Element class is a sequence of partitions with conditions
            on adjacent partitions in the sequence. This function checks
            that these conditions are met.
            """

        @abstract_method(optional=False)
        def _rule(self,p):
            """
            This is an abstract method. It must be overwritten in any
            Element class for this Category. This rule provides the
            functionality for this Category. It is called in local_rule.

            An instance of an Element class of this Category is a list
            of objects of some type. This function takes a list of length
            three of objects of this type and returns an object of this type.

            The key property is that the following operation on lists
            of length three is an involution: apply the rule to a list
            and replace the middle term with the output.
            """

################################# Book Keeping ################################
        def size(self):
            """
            Returns the size or length.
            """
            return len(self)

        def initial_shape(self):
            """
            Returns the initial shape.
            """
            return self[0]

        def final_shape(self):
            """
            Returns the final shape.
            """
            return self[-1]

############################# Jeu de taquin ###################################

        def local_rule(self,i):
            """
            This is the local that is used for the remaining constructions.
            This has input a list of objects. This method first takes
            the list of objects of length three consisting of the $(i-1)$-st,
            $i$-th and $(i+1)$-term and applies the rule. It then replaces
            the $i$-th object  by the object returned by the rule.
            """
            if not (i > 0 and i < len(self) ):
                raise ValueError("%d is not a valid integer." % i)

            result = list(self)
            result[i] = self._rule(self[i-1:i+2])

            return self.parent()(result)

        def promotion(self):
            """
            The promotion operator. This is given by a two row diagram.
            """
            result = list(self)
            for i in range(1,len(result)-1):
                result[i] = self._rule(result[i-1:i+2])
            return self.parent()(result)

        def evacuation(self):
            """
            The evacuation operator. This is given by a triangular diagram.
            """
            if self.size() < 3:
                return self

            T = self
            L = list(T)
            result = []
            for i in range(len(self)):
                T = self.parent()(L).promotion()
                L = list(T)
                result.append( L.pop() )
            result.reverse()
            return self.parent()(result)

        def commutor(self,other):
            """
            This constructs the commutor of a pair of tableau.
            This is given by a rectangular diagram.
            """
            n = len(self)
            m = len(other)

            row = list(self)
            col = list(other)
            for i in range(1,m):
                row[0] = self._rule([col[i-1],row[0],row[1]])
                for j in range(1,n):
                    row[j] = self._rule(row[i-1:i+2])

            return self.parent()(result) # Result is not defined.


        def cactus(self,i,j):
            """
            This constructs the action of the generators of the cactus group.
            These generators are involutions and are usually denoted by
            $s_{i,\,j$}$.
            """
            if not 0 < i < j < self.size():
                raise ValueError("Integers out of bounds.")

            if i == j:
                return self

            if i == 1:
                h = list(self)[:j-1]
                t = list(self)[j-1:]
                T = self.parent()(h)
                L = list(T.evacuation()) + t
                return self.parent()(L)

            return self.cactus(1,j).cactus(1,j-i).cactus(1,j)

########################### Visualisation and checking ########################

        def cylindrical_diagram(self):
            """
            This constructs the cylindrical growth diagram. This provides
            a visual summary of several operations simultaneously. The
            operations which can be read off directly from this diagram
            are the powers of the promotion operator (which form the rows)
            and the cactus group operators $s_{1,\,j$}$ (which form the
            first half of the columns).
            """
            n = len(self)
            result = [[None]*(2*n-1)]*n
            T = self
            for i in range(n):
                result[i] = [None]*i + list(T)
                T = T.promotion()

            return result

        def check_involution_rule(self):
            """
            This is to check that the local rule gives an involution.
            This is crucial.
            """
            for i in range(self.size()-2):
                if self.local_rule(i+1).local_rule(i+1) != self:
                    return False
            return True

        def check_involution_cactus(self):
            """
            This is to check that the cactus group generators are
            involutions..
            """
            return all([ self.cactus(1,i).cactus(1,i) == self for i in range(2,self.size() ) ])

        def check_promotion(self):
            """
            Promotion can be expressed in terms of the cactus generators.
            Here we check this relation.
            """
            n = self.size()
            lhs = self.promotion()
            rhs = self.cactus(1,n).cactus(2,n)
            return lhs == rhs

        def check_commutation(self):
            """
            This is to check the commutation relations in the presentation
            of the cactus group.
            """
            from itertools import combinations

            n = self.size()
            for i,j,r,s in combinations(range(n),4):
                lhs = self.cactus(i,j).cactus(r,s)
                rhs = self.cactus(r,s).cactus(i,j)
                if lhs != rhs:
                    return False
            return True

        def check_coboundary(self):
            """
            This is to check the coboundary relations in the presentation
            of the cactus group.
            """
            from itertools import combinations

            n = self.size()
            for i,j,r,s in combinations(range(n),4):
                lhs = self.cactus(i,s).cactus(j,r)
                rhs = self.cactus(i+s-r,i+s-j).cactus(i,s)
                if lhs != rhs:
                    return False
            return True

        def check_consistent(self):
            """
            This checks that two different constructions of the
            operators $s_{1,\,i}$ give the same result. The first
            construction is the direct construction which uses
            evacuation. The second method reads this off the
            cylindrical diagram; which is constructed using promotion.
            """
            d = self.cylindrical_diagram()
            for i in range(1,n):
                t = [ d[i][i-j] for j in range(i-1) ]
                x = self.parent()(t+d[0][i:])
                if x != self.cactus(1,i):
                    return False
            return True


        def orbit(self):
            """
            Constructs the orbit under the action of the cactus group.
            """
            n = self.size()
            orb = set([])
            rec = set([self])
            new = set([])
            while rec != set([]):
                for a in rec:
                    for i in range(self.size()):
                        b = a.cactus(1,i+1)
                        if b not in orb and b not in rec:
                            new.add(b)
                orbit.join(new)
                rec = copy(new)
                new = set([])

            return orb

        def dual_equivalence_graph(self):
            """
            This constructs the graph with vertices the orbit of self
            and edges given by the action of the cactus group generators.

            In most implementations the generators $s_{i,\,i+1}$ will act
            as the identity operators. The usual dual equivalence graphs
            are given by replacing the label $i,i+2$ by $i$ and removing
            edges with other labels.
            """
            from sage.graphs.graph import Graph
            from itertools import combinations

            G = Graph()
            orb = orbit(self)

            for a in orb:
                for i,j in combinations(range(self.size(),2)):
                    b = a.cactus(i+1,j+1)
                    if a != b:
                        G.add_edge(a,b,"%d,%d" % (i,j))
            return G

        def csp(self):
            import sage.combinat.cyclic_sieving_phenomenon

#### These functions don't belong here but I don't have a home for them. ####

        def drawL(self):
            """
            This assumes we have a sequence of partitions.
            This is the default case but need not always be the case.

            This draws a plot of the sequence of partitions.
            """

            gap = 1

            def draw_partition(p,origin):

                global gap

                if p == Partition([]):
                    return point(origin,axes=False,size=60)

                r = origin[0]
                s = origin[1]

                u = p.to_dyck_word()
                u = u[u.index(0):]
                u.reverse()
                u = u[u.index(1):]
                u.reverse()
                x = u.count(0)
                y = u.count(1)

                gap = max(x,gap)
                n = len(u)

                edge = []
                edge.append([r,-y+s])
                for i in range(n):
                    v = copy(edge[i])
                    if u[i] == 1:
                        v[1] += 1
                    else:
                        v[0] += 1
                    edge.append(v)

                G = Graphics()
                G += line([(r,-y+s),(r,s),(r+x,s)],axes=False,thickness=2)
                G += line(edge,color='red',axes=False,thickness=3)

                for i, a in enumerate(p[1:]):
                    G += line([(r,s-i-1),(r+a,s-i-1)],color='green')

                for i, a in enumerate(p.conjugate()[1:]):
                    G += line([(r+i+1,s),(r+i+1,s-a)],color='green')

                return G

            G = Graphics()

            for i, x in enumerate(self):
                G += draw_partition(x, (i*gap+1.5*i,0))

            G.set_aspect_ratio(1)

            return G

        def drawC(self):
            """
            This assumes we have a sequence of partitions.
            This is the default case but need not always be the case.

            This draws a plot of the sequence of partitions.
            """

            def draw_partition(p):

                if p == Partition([]):
                    return point((0,0),axes=False,size=60)

                u = p.to_dyck_word()
                u = u[u.index(0):]
                u.reverse()
                u = u[u.index(1):]
                u.reverse()
                x = u.count(0)
                y = u.count(1)

                n = len(u)

                edge = []
                edge.append([0,-y])
                for i in range(n):
                    v = copy(edge[i])
                    if u[i] == 1:
                        v[1] += 1
                    else:
                        v[0] += 1
                    edge.append(v)

                return line(edge,color='red',axes=False,thickness=3)

            p = self.final_shape()

            G = line([(0,-len(p)),(0,0),(p[0],0)],axes=False)

            for i, a in enumerate(p[1:]):
                G += line([(0,-i-1),(a,-i-1)],color='green')

            for i, a in enumerate(p.conjugate()[1:]):
                G += line([(i+1,0),(i+1,-a)],color='green')

            for i, x in enumerate(self):
                G += draw_partition(x)

            for p in self:
                G += draw_partition(p)

            G.set_aspect_ratio(1)

            return G
