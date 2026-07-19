FROM node:20-slim

WORKDIR /app

# העתקת קבצי הניהול של npm והתקנת חבילות
COPY ./front-end/package*.json ./
RUN npm install

# העתקת שאר קוד האתר
COPY ./front-end .

EXPOSE 5173

# הרצת שרת הפיתוח של Vite ומציאתו מחוץ לקונטיינר
CMD ["npm", "run", "dev", "--", "--host"]