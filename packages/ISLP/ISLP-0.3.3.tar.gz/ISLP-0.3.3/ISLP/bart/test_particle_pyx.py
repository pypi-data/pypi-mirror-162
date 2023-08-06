class mybuilder(PriorTreeBuilder):
    
    def split_prob(self, depth):
        return 0.6
    
    
from sklearn.tree._tree import Tree

mytree = Tree(10, np.array([1,1]), 2)
print(mytree.capacity, mytree.node_count)
pt = mybuilder(X.shape[1], 0)
mytree = pt.build(mytree, X, y, np.ones_like(y))
# -

(mytree.children_left,mytree.children_right)

mytree.threshold

mytree.feature

mytree.predict(X.astype(np.float32))

tree.plot_tree(mytree)
plt.show()

# +
n_nodes = mytree.node_count
children_left = mytree.children_left
children_right = mytree.children_right
feature = mytree.feature
threshold = mytree.threshold

node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
is_leaves = np.zeros(shape=n_nodes, dtype=bool)
stack = [(0, 0)]  # start with the root node id (0) and its depth (0)
while len(stack) > 0:
    # `pop` ensures each node is only visited once
    node_id, depth = stack.pop()
    node_depth[node_id] = depth

    # If the left and right child of a node is not the same we have a split
    # node
    is_split_node = children_left[node_id] != children_right[node_id]
    # If a split node, append left and right children and depth to `stack`
    # so we can loop through them
    if is_split_node:
        stack.append((children_left[node_id], depth + 1))
        stack.append((children_right[node_id], depth + 1))
    else:
        is_leaves[node_id] = True

print(
    "The binary tree structure has {n} nodes and has "
    "the following tree structure:\n".format(n=n_nodes)
)
for i in range(n_nodes):
    if is_leaves[i]:
        print(
            "{space}node={node} is a leaf node.".format(
                space=node_depth[i] * "\t", node=i
            )
        )
    else:
        print(
            "{space}node={node} is a split node: "
            "go to node {left} if X[:, {feature}] <= {threshold} "
            "else to node {right}.".format(
                space=node_depth[i] * "\t",
                node=i,
                left=children_left[i],
                feature=feature[i],
                threshold=threshold[i],
                right=children_right[i],
            )
        )
# -

     
                if parent != _TREE_UNDEFINED:
                    if is_left:
                        tree.nodes[parent].left_child = node_id
                        print(parent, node_id, 'left child')
                    else:
                        tree.nodes[parent].right_child = node_id
                        print(parent, node_id, 'right child')

                print(node_id, 'node')
                print(split, 'split')
                print(tree.children_left, 'left')
                print(tree.children_right, 'right')
                print(tree.feature, 'feature')
                print(tree.threshold, 'threshold')
                            
        
                # Push right child on stack
                if split:
                    builder_stack.push({
                        "depth": depth + 1,
                        "parent": node_id,
                        "is_left": 0,
                        "leaf_flag": True,
                        "try_split": True})

                    # Push left child on stack
                    builder_stack.push({
                        "depth": depth + 1,
                        "parent": node_id,
                        "is_left": 1,
                        "leaf_flag": True,
                        "try_split": True})
                    
