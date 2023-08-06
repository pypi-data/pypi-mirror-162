"""Surface Area of 3d shapes"""


def surface_area_cuboid(w: int | float, h: int | float, d: int | float) -> float:
    """
    Finds the surface area of a cuboid

    :param w: width of shape
    :param h: height of shape
    :param d: depth of shape
    :return:
    """
    if w < 0 or h < 0 or d < 0:
        raise ValueError("surface_area_cuboid() only accepts non-negative values")
    return 2 * (w * h + w * d + h * d)


def surface_area_cylinder(r: int | float, h: int | float) -> float:
    """
    Finds the surface area of a cylinder
    
    :param r: radius of shape
    :param h: height of shape
    :return: 
    """
    if r < 0 or h < 0:
        raise ValueError("surface_area_cylinder() only accepts non-negative values")
    return 2 * 3.141592653589793 * r * h + 2 * 3.141592653589793 * r**2


def surface_area_cube(a: int | float) -> float:
    """
    Finds the surface area of a cube

    :param a: length of shape
    :return:
    """
    if a < 0:
        raise ValueError("surface_area_cube() only accepts non-negative values")
    return 6 * a**2


def surface_area_sphere(r: int | float) -> float:
    """
    Finds the surface area of a sphere
    
    :param r: radius of shape
    :return: 
    """
    if r < 0:
        raise ValueError("surface_area_sphere() only accepts non-negative values")
    return 4 * 3.141592653589793 * r**2


def surface_area_pyramid_square(a: int | float, h: int | float) -> float:
    """
    Finds the surface area of a square pyramid

    :param a: length of shape
    :param h: perpendicular height of shape
    :return:
    """
    if a < 0 or h < 0:
        raise ValueError("surface_area_pyramid_square() only accepts non-negative values")
    return a**2 + 4 * a * h / 2


def surface_area_pyramid_triangle(a: int | float, h: int | float) -> float:
    """
    Finds the surface area of a square pyramid

    :param a: length of shape
    :param h: perpendicular height of shape
    :return:
    """
    if a < 0 or h < 0:
        raise ValueError("surface_area_pyramid_triangle() only accepts non-negative values")
    return 4 * a * h / 2


def surface_area_hemisphere(radius: float) -> float:
    """
    Finds the surface area of a hemisphere

    :param radius:
    :return:
    """
    if radius < 0:
        raise ValueError("surface_area_hemisphere() only accepts non-negative values")
    return 3 * 3.141592653589793 * radius**2


def surface_area_cone(radius: float, height: float) -> float:
    """
    Finds the surface area of a cone

    :param radius:
    :param height:
    :return:
    """
    if radius < 0 or height < 0:
        raise ValueError("surface_area_cone() only accepts non-negative values")
    return 3.141592653589793 * radius * (radius + (height**2 + radius**2) ** 0.5)


# TODO: function for a nth based pyramid, nth based prism, ovular cylinder, cone, ovular cone, ovular torus, torus,
#  nth based cylinder, nth based polygon


if __name__ == '__main__':
    pass
