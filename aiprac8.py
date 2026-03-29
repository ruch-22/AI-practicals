def fuzzy_union(fuzzy_set_A, fuzzy_set_B):
    """
    Computes the union of two fuzzy sets.
    The membership degree of an element in the union is the maximum of its
    membership degrees in the individual sets.
    """
    union_set = {}
    all_elements = set(fuzzy_set_A.keys()).union(fuzzy_set_B.keys())
    for element in all_elements:
        membership_A = fuzzy_set_A.get(element, 0.0)
        membership_B = fuzzy_set_B.get(element, 0.0)
        union_set[element] = max(membership_A, membership_B)
    return union_set

def fuzzy_intersection(fuzzy_set_A, fuzzy_set_B):
    """
    Computes the intersection of two fuzzy sets.
    The membership degree of an element in the intersection is the minimum of its
    membership degrees in the individual sets.
    """
    intersection_set = {}
    common_elements = set(fuzzy_set_A.keys()).intersection(fuzzy_set_B.keys())
    for element in common_elements:
        membership_A = fuzzy_set_A.get(element, 0.0)
        membership_B = fuzzy_set_B.get(element, 0.0)
        intersection_set[element] = min(membership_A, membership_B)
    return intersection_set

def fuzzy_complement(fuzzy_set):
    """
    Computes the complement of a fuzzy set.
    The membership degree of an element in the complement is 1 minus its
    membership degree in the original set.
    """
    complement_set = {}
    for element, membership_degree in fuzzy_set.items():
        complement_set[element] = 1.0 - membership_degree
    return complement_set

# Example Usage
if __name__ == "__main__":
    # Define two fuzzy sets as dictionaries (element: membership_degree)
    fuzzy_A = {"apple": 0.8, "banana": 0.3, "orange": 0.6, "grape": 0.1}
    fuzzy_B = {"banana": 0.7, "orange": 0.4, "kiwi": 0.9, "grape": 0.5}

    print("Fuzzy Set A:", fuzzy_A)
    print("Fuzzy Set B:", fuzzy_B)

    # Perform fuzzy union
    union_result = fuzzy_union(fuzzy_A, fuzzy_B)
    print("\nFuzzy Union (A U B):", union_result)

    # Perform fuzzy intersection
    intersection_result = fuzzy_intersection(fuzzy_A, fuzzy_B)
    print("Fuzzy Intersection (A ∩ B):", intersection_result)

    # Perform fuzzy complement on A
    complement_A_result = fuzzy_complement(fuzzy_A)
    print("Fuzzy Complement of A (A'):", complement_A_result)