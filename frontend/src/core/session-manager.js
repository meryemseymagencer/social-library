export const sessionManager = {
  getCurrentUser() {
    const data = localStorage.getItem("user");
    return data ? JSON.parse(data) : null;
  },

  getCurrentUserId() {
    const user = this.getCurrentUser();
    return user ? user.id : null;
  },

  saveUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
  },

  clearUser() {
    localStorage.removeItem("user");
  }
};
