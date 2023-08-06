from __future__ import annotations
from copy import deepcopy
from math import sqrt

class Vector3D:
  """
  A class to represent a vector in 3D space.

  ...
  Attributes
  ----------
    x: float
      the x position of the vector
    y: float
      the y position of the vector
    z: float
      the z position of the vector
  
  Methods
  ----------
    copy():
      Returns a copy of the vector.
    show():
      Prints visual representation of the vector.
    add():
      Returns the result of vector addition.
    subtract():
      Returns the result of vector subtraction.
    multiply():
      Returns a vector multiplied by a scalar value.
    divide():
      Returns a vector divided by a scalar value.
    dot():
      Returns the dot product between two vectors.
    cross():
      Returns the cross product between two vectors.
    magnitude():
      Returns the magnitude of the vector.
    normalize():
      Returns the normalized unit vector.
  """

  def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
    """
    Constructs all necessary attributes for the Vector3D object

    Parameters
    ----------
      x: float
        the x position of the vector
      y: float
        the y position of the vector
      z: float
        the z position of the vector
      
    Returns
    ----------
      None
    """

    self.x = x
    self.y = y
    self.z = z

  def __repr__(self) -> str:
    return f"{self.__class__.__name__} (x={self.x} y={self.y} z={self.z})"

  def __add__(self, v: Vector3D) -> Vector3D:
    return Vector3D(
      self.x + v.x,
      self.y + v.y,
      self.z + v.z,
    )

  def __sub__(self, v:  Vector3D) -> Vector3D:
    return Vector3D(
      self.x - v.x,
      self.y - v.y,
      self.z - v.z,
    )

  def __mul__(self, k: float) -> Vector3D:
    return Vector3D(
      k * self.x,
      k * self.y,
      k * self.z,
    )

  def __truediv__(self, k: float) -> Vector3D:
    return Vector3D(
      self.x / k,
      self.y / k,
      self.z / k,
    )

  def copy(self) -> Vector3D:
    """
    Returns a copy of the vector.

    Parameters
    ----------
      None

    Returns
    ----------
      (Vector3D) the copied vector
    """
    return deepcopy(self)

  def show(self) -> None:
    """
    Prints the vector.

    Parameters
    ----------
      None

    Returns
    ----------
      None
    """

    print(f"[{self.x} {self.y} {self.z}]")

  def add(self, v: Vector3D) -> Vector3D:
    """
    Returns the result of vector addition.

    Parameters
    ----------
      v: Vector3D
        the vector to be added 

    Returns
    ----------
      (Vector3D) the resulting vector
    """
    return Vector3D(
      self.x + v.x,
      self.y + v.y,
      self.z + v.z,
    )

  def subtract(self, v:  Vector3D) -> Vector3D:
    """
    Returns the result of vector subtraction.

    Parameters
    ----------
      v: Vector3D
        the vector to be subtracted

    Returns
    ----------
      (Vector3D) the resulting vector
    """
    return Vector3D(
      self.x - v.x,
      self.y - v.y,
      self.z - v.z,
    )

  def multiply(self, k: float) -> Vector3D:
    """
    Returns a vector multiplied by a scalar value.

    Parameters
    ----------
      k: float
        scaler value to multply by

    Returns
    ----------
      (Vector3D) the resulting vector
    """
    return Vector3D(
      k * self.x,
      k * self.y,
      k * self.z,
    )

  def divide(self, k: float) -> Vector3D:
    """
    Returns a vector divided by a scalar value.

    Parameters
    ----------
      k: float
        scaler value to divide by

    Returns
    ----------
      (Vector3D) the resulting vector
    """
    return Vector3D(
      self.x / k,
      self.y / k,
      self.z / k,
    )

  def dot(self, v: Vector3D) -> float:
    """
    Returns the dot product between two vectors. This value represents
    the angle between two vectors.

    Parameters
    ----------
      v: Vector3D
        the vector to calculate dot product with

    Returns
    ----------
      (float) the angle between vectors
    """
    return self.x * v.x + self.y * v.y + self.x * v.z

  def cross(self, v: Vector3D) -> Vector3D:
    """
    Returns the cross product between two vectors. This value represents a vector
    that is perpendicular to two vectors.

    Parameters
    ----------
      v: Vector3D
        the vector to calculate cross product with

    Returns
    ----------
      (Vector3D) the resulting vector
    """
    return Vector3D(
      self.y * v.z - self.z * v.y,
      self.z * v.x - self.x * v.z,
      self.x * v.y - self.y * v.x,
    )

  def magnitude(self) -> float:
    """
    Returns the magnitude of the vector.

    Parameters
    ----------
      None

    Returns
    ----------
      (float) the magnitude of the vector
    """
    return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

  def normalize(self) -> Vector3D:
    """
    Returns the normalized unit vector.

    Parameters
    ----------
      None

    Returns
    ----------
      (Vector3D) the unit vector
    """
    m = self.magnitude()

    if (m > 0.0):
      factor = 1.0 / m
      return Vector3D(
        factor * self.x,
        factor * self.y,
        factor * self.z,
      )
    else:
      return Vector3D()
