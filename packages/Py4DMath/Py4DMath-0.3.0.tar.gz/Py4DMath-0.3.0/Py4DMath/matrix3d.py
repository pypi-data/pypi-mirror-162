from __future__ import annotations
from copy import deepcopy

from .vector3d import Vector3D

class Matrix3D:
  """
  A class to represent a 3x3 matrix.

  ...
  Attributes
  ----------
    matrix: float[9]
      the array representing the matrix (column-major format)

  Class Methods
  ----------
    identity():
      Returns an identity matrix.

  Methods
  ----------
    copy():
      Returns a copy of the matrix.
    show():
      Prints visual representation of matrix.
    add():
      Returns the result of matrix addition.
    subtract():
      Returns the result of matrix subtraction.
    scalar_multiply():
      Returns a vector multiplied by a scalar value.
    matrix_multiply():
      Returns a vector multiplied by another matrix.
    inverse():
      Returns the inverse of the matrix.
    transpose():
      Returns the transpose of the matrix.
    transform():
      Returns vector transformed by matrix.
    setAsIdentityMatrix():
      Sets matrix as an identity matrix.
  """

  @staticmethod
  def identity(cls) -> Matrix3D:
    """
    Returns an identity matrix.

        1 0 0
    I = 0 1 0
        0 0 1 

    Parameters
    ----------
      None

    Returns
    ----------
      None
    """
    return Matrix3D(1, 0, 0, 0, 1, 0, 0, 0, 1)

  def __init__(self, m0: float = 0, m3: float = 0, m6: float = 0, m1: float = 0, m4: float = 0, m7: float = 0, m2: float = 0, m5: float = 0, m8: float = 0):
    """
    Constructs all necessary attributes for the Matrix3D object.

      0  3  6
      1  4  7   -> [0 1 2 3 4 5 6 7 8]
      2  5  8

    Parameters
    ----------
      m0: float
        the value at x=0, y=0
      m3: float
        the value at x=0, y=1
      m6: float
        the value at x=0, y=2
      m1: float
        the value at x=1, y=0
      m4: float
        the value at x=1, y=1
      m7: float
        the value at x=1, y=2
      m2: float
        the value at x=2, y=0
      m5: float
        the value at x=2, y=1
      m8: float
        the value at x=2, y=2

    Returns
    ----------
      None
    """
    self.matrix = [0.0]*9

    self.matrix[0] = m0
    self.matrix[3] = m3
    self.matrix[6] = m6

    self.matrix[1] = m1
    self.matrix[4] = m4
    self.matrix[7] = m7

    self.matrix[2] = m2
    self.matrix[5] = m5
    self.matrix[8] = m8

  def __repr__(self) -> str:
    return f"{self.__class__.__name__} (matrix={self.matrix})"

  def __add__(self, m: Matrix3D) -> Matrix3D:
    return Matrix3D(
      self.matrix[0] + m.matrix[0],
      self.matrix[3] + m.matrix[3],
      self.matrix[6] + m.matrix[6],
      self.matrix[1] + m.matrix[1],
      self.matrix[4] + m.matrix[4],
      self.matrix[7] + m.matrix[7],
      self.matrix[2] + m.matrix[2],
      self.matrix[5] + m.matrix[5],
      self.matrix[8] + m.matrix[8],
    )

  def __sub__(self, m: Matrix3D) -> Matrix3D:
    return Matrix3D(
      self.matrix[0] - m.matrix[0],
      self.matrix[3] - m.matrix[3],
      self.matrix[6] - m.matrix[6],
      self.matrix[1] - m.matrix[1],
      self.matrix[4] - m.matrix[4],
      self.matrix[7] - m.matrix[7],
      self.matrix[2] - m.matrix[2],
      self.matrix[5] - m.matrix[5],
      self.matrix[8] - m.matrix[8],
    )

  def __mul__(self, k: int or float or Matrix3D or Vector3D) -> Matrix3D or Vector3D:
    if isinstance(k, float) or isinstance(k, int):
      return Matrix3D(
        k * self.matrix[0],
        k * self.matrix[3],
        k * self.matrix[6],
        k * self.matrix[1],
        k * self.matrix[4],
        k * self.matrix[7],
        k * self.matrix[2],
        k * self.matrix[5],
        k * self.matrix[8],
      )
    elif isinstance(k, Matrix3D):
      return Matrix3D(
        self.matrix[0]*k.matrix[0] + self.matrix[3]*k.matrix[1] + self.matrix[6]*k.matrix[2],
        self.matrix[0]*k.matrix[3] + self.matrix[3]*k.matrix[4] + self.matrix[6]*k.matrix[5],
        self.matrix[0]*k.matrix[6] + self.matrix[3]*k.matrix[7] + self.matrix[6]*k.matrix[8],

        self.matrix[1]*k.matrix[0] + self.matrix[4]*k.matrix[1] + self.matrix[7]*k.matrix[2],
        self.matrix[1]*k.matrix[3] + self.matrix[4]*k.matrix[4] + self.matrix[7]*k.matrix[5],
        self.matrix[1]*k.matrix[6] + self.matrix[4]*k.matrix[7] + self.matrix[7]*k.matrix[8],

        self.matrix[2]*k.matrix[0] + self.matrix[5]*k.matrix[1] + self.matrix[8]*k.matrix[2],
        self.matrix[2]*k.matrix[3] + self.matrix[5]*k.matrix[4] + self.matrix[8]*k.matrix[5],
        self.matrix[2]*k.matrix[6] + self.matrix[5]*k.matrix[7] + self.matrix[8]*k.matrix[8],
      )
    elif isinstance(k, Vector3D):
      return Vector3D(
        self.matrix[0]*k.x+self.matrix[3]*k.y+self.matrix[6]*k.z,
        self.matrix[1]*k.x+self.matrix[4]*k.y+self.matrix[7]*k.z,
        self.matrix[2]*k.x+self.matrix[5]*k.y+self.matrix[8]*k.z,
      )
    else:
      raise TypeError(f"{type(k)} is not supported.")

  def copy(self) -> Matrix3D:
    """
    Returns a copy of the matrix.

    Parameters
    ----------
      None

    Returns
    ----------
      (Matrix3D) the copied matrix
    """
    return deepcopy(self)

  def show(self) -> None:
    """
    Prints the matrix in 3x3 grid.

    Parameters
    ----------
      None

    Returns
    ----------
      None
    """

    print(f"[{self.matrix[0]} {self.matrix[3]} {self.matrix[6]}]")
    print(f"[{self.matrix[1]} {self.matrix[4]} {self.matrix[7]}]")
    print(f"[{self.matrix[2]} {self.matrix[5]} {self.matrix[8]}]")

  def add(self, m: Matrix3D) -> Matrix3D:
    """
    Returns the result of matrix addition.

    Parameters
    ----------
      m: Matrix3D
        the matrix to be added 

    Returns
    ----------
      (Matrix3D) the resulting matrix
    """
    return Matrix3D(
      self.matrix[0] + m.matrix[0],
      self.matrix[3] + m.matrix[3],
      self.matrix[6] + m.matrix[6],
      self.matrix[1] + m.matrix[1],
      self.matrix[4] + m.matrix[4],
      self.matrix[7] + m.matrix[7],
      self.matrix[2] + m.matrix[2],
      self.matrix[5] + m.matrix[5],
      self.matrix[8] + m.matrix[8],
    )

  def subtract(self, m: Matrix3D) -> Matrix3D:
    """
    Returns the result of matrix subtraction.

    Parameters
    ----------
      m: Matrix3D
        the matrix to be subtracted

    Returns
    ----------
      (Matrix3D) the resulting matrix
    """
    return Matrix3D(
      self.matrix[0] - m.matrix[0],
      self.matrix[3] - m.matrix[3],
      self.matrix[6] - m.matrix[6],
      self.matrix[1] - m.matrix[1],
      self.matrix[4] - m.matrix[4],
      self.matrix[7] - m.matrix[7],
      self.matrix[2] - m.matrix[2],
      self.matrix[5] - m.matrix[5],
      self.matrix[8] - m.matrix[8],
    )

  def scalar_multiply(self, k: float) -> Matrix3D:
    """
    Returns a matrix multiplied by a scalar value.

    Parameters
    ----------
      k: float
        scaler value to multply by

    Returns
    ----------
      (Matrix3D) the resulting matrix
    """
    return Matrix3D(
      k * self.matrix[0],
      k * self.matrix[3],
      k * self.matrix[6],
      k * self.matrix[1],
      k * self.matrix[4],
      k * self.matrix[7],
      k * self.matrix[2],
      k * self.matrix[5],
      k * self.matrix[8],
    )


  def matrix_multiply(self, k: Matrix3D()) -> Matrix3D:
    """
    Returns a matrix multiplied by another matrix.

    Parameters
    ----------
      k:  Matrix3D
        matrix to multiply by

    Returns
    ----------
      (Matrix3D) the resulting matrix
    """
    return Matrix3D(
      self.matrix[0]*k.matrix[0] + self.matrix[3]*k.matrix[1] + self.matrix[6]*k.matrix[2],
      self.matrix[0]*k.matrix[3] + self.matrix[3]*k.matrix[4] + self.matrix[6]*k.matrix[5],
      self.matrix[0]*k.matrix[6] + self.matrix[3]*k.matrix[7] + self.matrix[6]*k.matrix[8],

      self.matrix[1]*k.matrix[0] + self.matrix[4]*k.matrix[1] + self.matrix[7]*k.matrix[2],
      self.matrix[1]*k.matrix[3] + self.matrix[4]*k.matrix[4] + self.matrix[7]*k.matrix[5],
      self.matrix[1]*k.matrix[6] + self.matrix[4]*k.matrix[7] + self.matrix[7]*k.matrix[8],

      self.matrix[2]*k.matrix[0] + self.matrix[5]*k.matrix[1] + self.matrix[8]*k.matrix[2],
      self.matrix[2]*k.matrix[3] + self.matrix[5]*k.matrix[4] + self.matrix[8]*k.matrix[5],
      self.matrix[2]*k.matrix[6] + self.matrix[5]*k.matrix[7] + self.matrix[8]*k.matrix[8],
    )

  def inverse(self) -> Matrix3D or None:
    """
    Returns the inverse of the matrix.

             m0 m3 m6 ^-1        1     A D G
    M^-1  =  m1 m4 m7      =    ---    B E H
             m2 m5 m8          det(M)  C F I

    A = m4m8 - m7m5   D = -(m3m8-m5m6)  G = m3m7-m4m6
    B = -(m1m8-m7m2)  E = m0m8-m6m2     H = -(m0m7-m1m6)
    C = m1m5-m4m2     F = -(m0m5-m3m2)  I = m0m4-m3m1

    det(M) = m0A + m3B + m6C

    Parameters
    ----------
      None

    Returns
    ----------
      (Matrix3D) the inverse of the matrix or None if invalid.
    """

    A = self.matrix[4]*self.matrix[8] - self.matrix[7]*self.matrix[5]
    B = -(self.matrix[1]*self.matrix[8] - self.matrix[7]*self.matrix[2])
    C = self.matrix[1]*self.matrix[5] - self.matrix[4] * self.matrix[2]
    D = -(self.matrix[3]*self.matrix[8] - self.matrix[5]*self.matrix[6])
    E = self.matrix[0]*self.matrix[8] - self.matrix[6]*self.matrix[2]
    F = -(self.matrix[0]*self.matrix[5] - self.matrix[3]*self.matrix[2])
    G = self.matrix[3]*self.matrix[7] - self.matrix[4]*self.matrix[6]
    H = -(self.matrix[0]*self.matrix[7] - self.matrix[1]*self.matrix[6])
    I = self.matrix[0]*self.matrix[4] - self.matrix[3]*self.matrix[1]

    det = self.matrix[0]*A + self.matrix[3]*B + self.matrix[6]*C

    if det == 0:
      return None

    det_inv = 1.0 / det

    return Matrix3D(
      det_inv*A,
      det_inv*B,
      det_inv*C,
      det_inv*D,
      det_inv*E,
      det_inv*F,
      det_inv*G,
      det_inv*H,
      det_inv*I,
    )

  def transpose(self) -> Matrix3D:
    """
    Returns the transpose of the matrix.

          m0 m3 m6              m0 m1 m2
    M  =  m1 m4 m7      M^T  =  m3 m4 m5
          m2 m5 m8              m6 m7 m8

    Parameters
    ----------
      None

    Returns
    ----------
      (Matrix3D) the transposed matrix.
    """
    return Matrix3D(
      self.matrix[0],
      self.matrix[1],
      self.matrix[2],
      self.matrix[3],
      self.matrix[4],
      self.matrix[5],
      self.matrix[6],
      self.matrix[7],
      self.matrix[8],
    )

  def transform(self, v: Vector3D) -> Vector3D:
    """
    Returns vector transformed by matrix.

    Parameters
    ----------
      v: (Vector3D) the vector to transform

    Returns
    ----------
      (Vector3D) the resulting vector
    """
    return Vector3D(
      self.matrix[0]*v.x+self.matrix[3]*v.y+self.matrix[6]*v.z,
      self.matrix[1]*v.x+self.matrix[4]*v.y+self.matrix[7]*v.z,
      self.matrix[2]*v.x+self.matrix[5]*v.y+self.matrix[8]*v.z,
    )

  def setAsIdentityMatrix(self):
    """
    Sets matrix as an identity matrix.

        1 0 0
    I = 0 1 0
        0 0 1 

    Parameters
    ----------
      None

    Returns
    ----------
      None
    """
    for i in range(9):
      self.matrix[i] = 0.0

    self.matrix[0] = self.matrix[4] = self.matrix[8] = 1.0
